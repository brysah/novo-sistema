"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AlertCircle, Trash2, Plus, Play, Square, RotateCcw, Zap, Turtle, Settings, Globe, Activity } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface Newsletter {
  id: string
  name: string
  url: string
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
  const [speed, setSpeed] = useState<"slow" | "fast">("slow")
  const [isRunning, setIsRunning] = useState(false)
  const [progress, setProgress] = useState<ProgressItem[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [backendConnected, setBackendConnected] = useState(false)
  const [activeTab, setActiveTab] = useState("automation")
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
      const response = await fetch(`${API_BASE_URL}/newsletters`)
      if (response.ok) {
        const data = await response.json()
        const newsletterList: Newsletter[] = data.newsletters.map((url: string, index: number) => ({
          id: (index + 1).toString(),
          name: new URL(url).hostname.replace('www.', ''),
          url: url
        }))
        setNewsletters(newsletterList)
      }
    } catch (error) {
      console.error("Error loading newsletters:", error)
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
          }
        }
      }
    } catch (error) {
      console.error("Error polling progress:", error)
    }
  }

  const addNewsletter = async () => {
    if (!newNewsletterUrl.trim()) return
    
    try {
      const response = await fetch(`${API_BASE_URL}/newsletters`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: newNewsletterUrl
        })
      })
      
      if (response.ok) {
        // Reload newsletters from backend
        await loadNewsletters()
        setNewNewsletterName("")
        setNewNewsletterUrl("")
      } else {
        const error = await response.json()
        alert(error.detail || "Failed to add newsletter")
      }
    } catch (error) {
      console.error("Error adding newsletter:", error)
      alert("Failed to add newsletter")
    }
  }

  const removeNewsletter = async (id: string) => {
    const newsletter = newsletters.find(n => n.id === id)
    if (!newsletter) return
    
    try {
      const response = await fetch(`${API_BASE_URL}/newsletters?url=${encodeURIComponent(newsletter.url)}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        // Reload newsletters from backend
        await loadNewsletters()
      } else {
        const error = await response.json()
        alert(error.detail || "Failed to remove newsletter")
      }
    } catch (error) {
      console.error("Error removing newsletter:", error)
      alert("Failed to remove newsletter")
    }
  }

  const startSubscriptions = async () => {
    const emailList = emails
      .split("\n")
      .map((e) => e.trim())
      .filter((e) => e && e.includes("@"))

    if (!emailList.length || !newsletters.length) {
      alert("Please add at least one email and one newsletter")
      return
    }

    if (!backendConnected) {
      alert("Backend server not connected. Make sure to run: python backend/main.py")
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          emails: emailList,
          urls: newsletters.map((n) => n.url),
          speed: speed,
        }),
      })

      if (response.ok) {
        setIsRunning(true)
        setProgress([])

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
      await fetch(`${API_BASE_URL}/stop`, { method: "POST" })
      setIsRunning(false)
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current)
    } catch (error) {
      console.error("Error stopping subscriptions:", error)
    }
  }

  const clearAll = () => {
    setEmails("")
    setProgress([])
    setCurrentIndex(0)
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
        return "✗ Error"
      case "http_error":
        return "✗ HTTP Error"
      case "no_email_field":
        return "✗ No Email Field"
      case "unknown_result":
        return "? Unknown"
      case "running":
        return "⟳ Running"
      default:
        return "Pending"
    }
  }

  const completedCount = progress.filter((p) => p.status !== "pending" && p.status !== "running").length
  const successCount = progress.filter((p) => p.status === "ok").length

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-4xl font-bold text-slate-900">Newsletter Automation</h1>
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${backendConnected ? "bg-green-500" : "bg-red-500"}`}></div>
              <span className="text-sm text-slate-600">
                {backendConnected ? "Backend Connected" : "Backend Disconnected"}
              </span>
            </div>
          </div>
          <p className="text-slate-600">Automate newsletter subscriptions with human-like behavior</p>
        </div>

        {/* Tabs Navigation */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-6">
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
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Emails Section */}
              <Card className="p-6 border-slate-200">
                <h2 className="text-lg font-semibold text-slate-900 mb-4">Emails</h2>
                <Textarea
                  placeholder="Enter emails (one per line)&#10;example1@email.com&#10;example2@email.com"
                  value={emails}
                  onChange={(e) => setEmails(e.target.value)}
                  className="min-h-32 resize-none"
                  disabled={isRunning}
                />
                <p className="text-xs text-slate-500 mt-2">
                  {emails.split("\n").filter((e) => e.trim() && e.includes("@")).length} valid emails
                </p>
              </Card>

              {/* Speed Section */}
              <Card className="p-6 border-slate-200">
                <h2 className="text-lg font-semibold text-slate-900 mb-4">Velocidade</h2>
                <div className="space-y-2">
                  <button
                    onClick={() => setSpeed("slow")}
                    disabled={isRunning}
                    className={`w-full p-3 rounded-lg border-2 transition-all flex items-center justify-center gap-2 ${
                      speed === "slow"
                        ? "border-slate-900 bg-slate-900 text-white"
                        : "border-slate-200 bg-white text-slate-900 hover:border-slate-300"
                    }`}
                  >
                    <Turtle className="w-5 h-5" />
                    <span className="font-medium">Lento & Seguro</span>
                  </button>
                  <button
                    onClick={() => setSpeed("fast")}
                    disabled={isRunning}
                    className={`w-full p-3 rounded-lg border-2 transition-all flex items-center justify-center gap-2 ${
                      speed === "fast"
                        ? "border-slate-900 bg-slate-900 text-white"
                        : "border-slate-200 bg-white text-slate-900 hover:border-slate-300"
                    }`}
                  >
                    <Zap className="w-5 h-5" />
                    <span className="font-medium">Rápido</span>
                  </button>
                </div>
                <p className="text-xs text-slate-500 mt-3">
                  {speed === "slow" ? "1 thread, 4-8s delays" : "2-3 threads, 1-2s delays"}
                </p>
              </Card>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4 justify-center">
              <Button
                onClick={startSubscriptions}
                disabled={isRunning || !emails.trim() || newsletters.length === 0 || !backendConnected}
                className="bg-green-600 hover:bg-green-700 text-white font-semibold py-6 px-8 text-lg"
              >
                <Play className="w-5 h-5 mr-2" />
                Rodar Subscrições
              </Button>
              <Button
                onClick={stopSubscriptions}
                disabled={!isRunning}
                variant="outline"
                className="border-red-300 text-red-600 hover:bg-red-50 bg-transparent py-6 px-8"
              >
                <Square className="w-5 h-5 mr-2" />
                Parar
              </Button>
              <Button 
                onClick={clearAll} 
                disabled={isRunning} 
                variant="outline" 
                className="bg-transparent py-6 px-8"
              >
                <RotateCcw className="w-5 h-5 mr-2" />
                Limpar
              </Button>
            </div>
          </TabsContent>

          {/* Tab Content: URLs */}
          <TabsContent value="urls">
            <Card className="p-6 border-slate-200">
              <h2 className="text-lg font-semibold text-slate-900 mb-4">Gerenciar URLs de Newsletter</h2>
              
              {/* Add Newsletter Form */}
              <div className="space-y-3 mb-6 p-4 bg-slate-50 rounded-lg">
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
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {newsletters.map((newsletter) => (
                      <div key={newsletter.id} className="flex items-center justify-between bg-white p-4 rounded-lg border border-slate-200 hover:shadow-sm transition-shadow">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-slate-900 truncate">{newsletter.name}</p>
                          <p className="text-xs text-slate-500 truncate">{newsletter.url}</p>
                        </div>
                        <button
                          onClick={() => removeNewsletter(newsletter.id)}
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
            <Card className="p-6 border-slate-200">
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
                  <div className="grid grid-cols-3 gap-4 p-4 bg-slate-50 rounded-lg">
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
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {progress.map((item, idx) => (
                      <div
                        key={idx}
                        className="flex items-start gap-3 p-4 bg-white rounded-lg border border-slate-200"
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

        {/* Info Alert */}
        <Alert className="mt-6 border-slate-200 bg-blue-50">
          <AlertCircle className="h-4 w-4 text-blue-600" />
          <AlertDescription className="text-slate-700">
            {backendConnected ? (
              <>Backend conectado. Delays e comportamento humanizado ajudam a evitar detecção de bot.</>
            ) : (
              <>
                Backend desconectado. Inicie o servidor Python com:{" "}
                <code className="bg-blue-100 px-2 py-1 rounded">python backend/main.py</code>
              </>
            )}
          </AlertDescription>
        </Alert>
      </div>
    </div>
  )
}
