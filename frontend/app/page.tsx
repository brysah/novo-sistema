"use client"

import { useState, useEffect, useRef } from "react"
import { toast } from "@/hooks/use-toast"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AlertCircle, Trash2, Plus, Play, Square, RotateCcw, Zap, Turtle, Settings, Globe, Activity } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface Newsletter {
  url: string
  name?: string
}

interface ProgressItem {
  email: string
  url: string
  status: "pending" | "ok" | "captcha" | "error" | "running" | "no_email_field" | "http_error" | "unknown_result"
  message?: string
}

const API_BASE_URL = "http://localhost:8000"

export default function Home() {
  const [emails, setEmails] = useState("")
  const [newsletters, setNewsletters] = useState<Newsletter[]>([])
  const [newNewsletterName, setNewNewsletterName] = useState("")
  const [newNewsletterUrl, setNewNewsletterUrl] = useState("") 
  const [isRunning, setIsRunning] = useState(false)
  const [progress, setProgress] = useState<ProgressItem[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [backendConnected, setBackendConnected] = useState(false)
  const [activeTab, setActiveTab] = useState("automation")
  const [stopToastFired, setStopToastFired] = useState(false)
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    checkBackendConnection()
    loadNewsletters()
    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current)
    }
  }, [])

  const checkBackendConnection = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/status`)
      if (response.ok) {
        setBackendConnected(true)
        loadNewsletters() // Load newsletters after connection is confirmed
      }
    } catch (error) {
      setBackendConnected(false)
    }
  }

  const loadNewsletters = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/newsletter/urls`)
      if (response.ok) {
        const data = await response.json()
        // O backend retorna { urls: [ ... ] }
        const newsletterList: Newsletter[] = data.urls.map((url: string) => ({
          url,
          name: url ? new URL(url).hostname.replace('www.', '') : ""
        }))
        setNewsletters(newsletterList)
      }
    } catch (error) {
      console.error("Erro ao carregar newsletters:", error)
    }
  }

  const pollProgress = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks`)
      if (response.ok) {
        const tasks = await response.json()
        const progressItems: ProgressItem[] = tasks.map((task: any) => ({
          email: task.email,
          url: task.url,
          status: task.status,
          message: task.message,
        }))
        setProgress(progressItems)

        // Check if still running
        const statusResponse = await fetch(`${API_BASE_URL}/status`)
        if (statusResponse.ok) {
          const status = await statusResponse.json()
          if (!status.is_running && isRunning) {
            setIsRunning(false)
            if (pollIntervalRef.current) clearInterval(pollIntervalRef.current)
            if (!stopToastFired) {
              setStopToastFired(true) 
              toast({
                  title: "Automação parada",
                  description: "O processo foi finalizado e você pode iniciar novamente.",
                  variant: "default"
                })
            }
          } else if (!status.is_running && !isRunning) {
            // Garante que nunca fica travado
            setIsRunning(false)
            if (pollIntervalRef.current) clearInterval(pollIntervalRef.current)
          }
        }
      }
    } catch (error) {
      console.error("Error polling progress:", error)
    }
  }

  const addNewsletter = async () => {
    if (!newNewsletterUrl.trim()) {
      toast({
        title: "URL inválida",
        description: "Digite uma URL de newsletter válida.",
        variant: "destructive"
      })
      return
    }
    // Validação simples de URL
    try {
      new URL(newNewsletterUrl.trim())
    } catch {
      toast({
        title: "URL inválida",
        description: "Digite uma URL de newsletter válida.",
        variant: "destructive"
      })
      return
    }
    const updatedUrls = [...newsletters.map(n => n.url), newNewsletterUrl.trim()]
    try {
      const response = await fetch(`${API_BASE_URL}/newsletter/urls`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ urls: updatedUrls })
      })
      if (response.ok) {
        await loadNewsletters()
        setNewNewsletterName("")
        setNewNewsletterUrl("")
      } else {
        toast({
          title: "Não foi possível adicionar",
          description: "A URL não foi aceita pelo backend.",
          variant: "destructive"
        })
      }
    } catch (error) {
      toast({
        title: "Erro ao adicionar newsletter",
        description: "Ocorreu um erro ao tentar adicionar a URL.",
        variant: "destructive"
      })
    }
  }

  const removeNewsletter = async (url: string) => {
    // Remove a URL da lista local e envia a lista inteira para o backend
    const updatedUrls = newsletters.map(n => n.url).filter(u => u !== url)
    try {
      const response = await fetch(`${API_BASE_URL}/newsletter/urls`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ urls: updatedUrls })
      })
      if (response.ok) {
        await loadNewsletters()
      } else {
        alert("Falha ao remover newsletter")
      }
    } catch (error) {
      alert("Erro ao remover newsletter")
    }
  }

  const startSubscriptions = async () => {
    const emailList = emails
      .split("\n")
      .map((e) => e.trim())
      .filter((e) => e && e.includes("@"))

    if (!emailList.length || !newsletters.length) {
      alert("Adicione pelo menos um email e uma newsletter")
      return
    }

    if (!backendConnected) {
      alert("Backend desconectado. Inicie o servidor Python com: python backend/main.py")
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          emails: emailList,
          urls: newsletters.map((n) => n.url)
        }),
      })

      if (response.ok) {
        setIsRunning(true)
        setProgress([])
        setStopToastFired(false)
        // Start polling for updates
        if (pollIntervalRef.current) clearInterval(pollIntervalRef.current)
        pollIntervalRef.current = setInterval(pollProgress, 1000)
      } else {
        alert("Failed to start subscriptions")
      }
    } catch (error) {
      alert("Error connecting to backend server")
      console.error(error)
    }
  }

  const stopSubscriptions = async () => {
    try {
      toast({
        title: "Parando automação...",
        description: "Aguarde alguns segundos para finalizar o processo.",
        variant: "default"
      })
      await fetch(`${API_BASE_URL}/stop`, { method: "POST" })
      // Não destrava aqui, espera polling detectar is_running: false
    } catch (error) {
      console.error("Error stopping subscriptions:", error)
    }
  }

  const clearAll = () => {
    setEmails("")
    setProgress([])
    setCurrentIndex(0)
  }

  const resetSystem = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/reset`, { method: "POST" })
      if (response.ok) {
        setIsRunning(false)
        setProgress([])
        setEmails("")
        setCurrentIndex(0)
        setStopToastFired(false)
        if (pollIntervalRef.current) clearInterval(pollIntervalRef.current)
        toast({
          title: "Sistema resetado",
          description: "O sistema foi resetado para o estado inicial."
        })
      }
    } catch (error) {
      console.error("Error resetting system:", error)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "ok":
        return "bg-green-100 text-green-800"
      case "captcha":
        return "bg-yellow-100 text-yellow-800"
      case "error":
      case "http_error":
      case "no_email_field":
      case "unknown_result":
        return "bg-red-100 text-red-800"
      case "running":
        return "bg-blue-100 text-blue-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "ok":
        return "✓ OK"
      case "captcha":
        return "⚠ CAPTCHA"
      case "error":
        return "✗ Erro"
      case "http_error":
        return "✗ HTTP Erro"
      case "no_email_field":
        return "✗ Sem Campo de E-mail"
      case "unknown_result":
        return "? Desconhecido"
      case "running":
        return "⟳ Processando"
      default:
        return "Pendente"
    }
  }

  const completedCount = progress.filter((p) => p.status !== "pending" && p.status !== "running").length
  const successCount = progress.filter((p) => p.status === "ok").length

  return (
  <div className="min-h-screen bg-linear-to-br from-slate-50 to-slate-100 p-2 sm:p-4 md:p-6">
    <div className="max-w-6xl mx-auto w-full">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-2 gap-2">
            <h1 className="text-2xl sm:text-4xl font-bold text-slate-900">Newsletter Automação</h1>
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${backendConnected ? "bg-green-500" : "bg-red-500"}`}></div>
              <span className="text-xs sm:text-sm text-slate-600">
                {backendConnected ? "Backend Conectado" : "Backend Disconectado"}
              </span>
            </div>
          </div>
        </div>

        {/* Tabs Navigation */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-1 sm:grid-cols-3 mb-6">
            <TabsTrigger value="automation" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Automação
            </TabsTrigger>
            <TabsTrigger value="urls" className="flex items-center gap-2">
              <Globe className="w-4 h-4" />
              URLs
            </TabsTrigger>
            <TabsTrigger value="progress" className="flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Progresso
            </TabsTrigger>
          </TabsList>

          {/* Tab Content: Automação */}
          <TabsContent value="automation" className="space-y-6">
            <div className="grid grid-cols-1 gap-6">
              {/* Emails Section */}
              <Card className="p-4 sm:p-6 border-slate-200">
                <h2 className="text-lg font-semibold text-slate-900 mb-4">Emails</h2>
                <Textarea
                  placeholder="Digite os emails (um por linha)"
                  value={emails}
                  onChange={(e) => setEmails(e.target.value)}
                  className="min-h-24 sm:min-h-32 resize-none text-sm"
                  disabled={isRunning}
                />
                <p className="text-xs text-slate-500 mt-2">
                  {emails.split("\n").filter((e) => e.trim() && e.includes("@")).length} emails válidos
                </p>
              </Card>
 
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-2 sm:gap-4 justify-center">
              <Button
                onClick={startSubscriptions}
                disabled={isRunning || !emails.trim() || newsletters.length === 0 || !backendConnected}
                className="bg-green-600 hover:bg-green-700 text-white font-semibold py-4 sm:py-6 px-4 sm:px-8 text-base sm:text-lg w-full sm:w-auto"
              >
                <Play className="w-5 h-5 mr-2" />
                Rodar Inscrições
              </Button>
              <Button
                onClick={stopSubscriptions}
                disabled={!isRunning}
                variant="outline"
                className="border-red-300 text-red-600 hover:bg-red-50 bg-transparent py-4 sm:py-6 px-4 sm:px-8 w-full sm:w-auto"
              >
                <Square className="w-5 h-5 mr-2" />
                Parar
              </Button>
              <Button 
                onClick={clearAll} 
                disabled={isRunning} 
                variant="outline" 
                className="bg-transparent py-4 sm:py-6 px-4 sm:px-8 w-full sm:w-auto"
              >
                <RotateCcw className="w-5 h-5 mr-2" />
                Limpar
              </Button>
            </div>
          </TabsContent>

          {/* Tab Content: URLs */}
          <TabsContent value="urls">
            <Card className="p-4 sm:p-6 border-slate-200">
              <h2 className="text-lg font-semibold text-slate-900 mb-4">Gerenciar URLs de Newsletter</h2>
              
              {/* Add Newsletter Form */}
              <div className="space-y-3 mb-6 p-2 sm:p-4 bg-slate-50 rounded-lg">
                <Input
                  placeholder="Nome da Newsletter (opcional)"
                  value={newNewsletterName}
                  onChange={(e) => setNewNewsletterName(e.target.value)}
                  disabled={isRunning}
                  className="text-sm"
                />
                <Input
                  placeholder="URL da Newsletter"
                  value={newNewsletterUrl}
                  onChange={(e) => setNewNewsletterUrl(e.target.value)}
                  disabled={isRunning}
                  className="text-sm"
                />
                <Button
                  onClick={addNewsletter}
                  disabled={isRunning || !newNewsletterUrl.trim()}
                  className="w-full bg-slate-900 hover:bg-slate-800"
                  size="sm"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Adicionar Newsletter
                </Button>
              </div>

              {/* Newsletter List */}
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <h3 className="text-md font-medium text-slate-700">Newsletters Cadastradas</h3>
                  <span className="text-sm text-slate-500">
                    {newsletters.length} newsletter{newsletters.length !== 1 ? "s" : ""}
                  </span>
                </div>
                
                {newsletters.length === 0 ? (
                  <div className="text-center py-8 text-slate-500">
                    <Globe className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>Nenhuma newsletter cadastrada</p>
                    <p className="text-sm">Adicione URLs para começar</p>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-64 sm:max-h-96 overflow-y-auto">
                    {newsletters.map((newsletter) => (
                      <div key={newsletter.url} className="flex items-center justify-between bg-white p-4 rounded-lg border border-slate-200 hover:shadow-sm transition-shadow">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-slate-900 truncate">{newsletter.name}</p>
                          <p className="text-xs text-slate-500 truncate">{newsletter.url}</p>
                        </div>
                        <button
                          onClick={() => removeNewsletter(newsletter.url)}
                          className="ml-3 p-2 hover:bg-red-50 rounded transition-colors text-red-600"
                          disabled={isRunning}
                          title="Remover newsletter"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </Card>
          </TabsContent>

          {/* Tab Content: Progresso */}
          <TabsContent value="progress">
            <Card className="p-4 sm:p-6 border-slate-200">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold text-slate-900">Progresso da Automação</h2>
                {progress.length > 0 && (
                  <div className="text-sm text-slate-600">
                    {completedCount} / {progress.length} ({Math.round((completedCount / progress.length) * 100)}%)
                  </div>
                )}
              </div>

              {progress.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-96 text-slate-500">
                  <Activity className="w-16 h-16 mb-4 opacity-50" />
                  <p className="text-lg mb-2">Nenhuma automação em andamento</p>
                  <p className="text-sm">Vá para a aba "Automação" para começar</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Progress Statistics */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 p-2 sm:p-4 bg-slate-50 rounded-lg">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-green-600">{successCount}</p>
                      <p className="text-xs text-slate-600">Sucesso</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-yellow-600">
                        {progress.filter((p) => p.status === "captcha").length}
                      </p>
                      <p className="text-xs text-slate-600">CAPTCHA</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-red-600">
                        {
                          progress.filter(
                            (p) =>
                              p.status !== "ok" &&
                              p.status !== "captcha" &&
                              p.status !== "pending" &&
                              p.status !== "running",
                          ).length
                        }
                      </p>
                      <p className="text-xs text-slate-600">Falhas</p>
                    </div>
                  </div>

                  {/* Progress List */}
                  <div className="space-y-2 max-h-64 sm:max-h-96 overflow-y-auto">
                    {progress.map((item, idx) => (
                      <div
                        key={idx}
                        className="flex flex-col sm:flex-row items-start gap-2 sm:gap-3 p-3 sm:p-4 bg-white rounded-lg border border-slate-200"
                      >
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-medium text-slate-500">
                              {idx + 1} / {progress.length}
                            </span>
                            <Badge className={`${getStatusColor(item.status)} text-xs`}>
                              {getStatusLabel(item.status)}
                            </Badge>
                          </div>
                          <p className="text-sm font-medium text-slate-900 truncate">{item.email}</p>
                          <p className="text-xs text-slate-600 truncate">{item.url}</p>
                          {item.message && <p className="text-xs text-slate-500 mt-1">{item.message}</p>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </Card>
          </TabsContent>
        </Tabs>
 
      </div>
    </div>
  )
}
