# Migração do formato de newsletters.json

Agora o backend armazena newsletters como objetos `{id, url}`. Na primeira execução após a atualização, qualquer string antiga será automaticamente convertida para o novo formato. Não é necessário migrar manualmente.

- Exclusão e manipulação agora são feitas por `id`.
- O endpoint DELETE mudou para `/newsletters/{id}`.
- O endpoint POST espera o campo `url` no corpo (JSON).

Se precisar resetar, basta apagar o arquivo `newsletters.json` (ele será recriado vazio).
