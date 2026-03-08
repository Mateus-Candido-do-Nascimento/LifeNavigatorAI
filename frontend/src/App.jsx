import { useState, useEffect, useRef } from "react"
import axios from "axios"

const SESSION_ID = crypto.randomUUID()
const API_URL = import.meta.env.VITE_API_URL

export default function App() {
  const [mensagens, setMensagens] = useState([
    {
      id: crypto.randomUUID(),
      role: "assistant",
      content: "Olá! Sou o LifeNavigator AI. Posso te ajudar com análises sobre concurso público e custo de vida em São Paulo. Como posso ajudar?",
    },
  ])
  const [input, setInput] = useState("")
  const [carregando, setCarregando] = useState(false)
  const fimDaListaRef = useRef(null)

  // auto-scroll sempre que chegar nova mensagem
  useEffect(() => {
    fimDaListaRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [mensagens])

  async function enviarMensagem() {
    if (!input.trim() || carregando) return

    const mensagemUsuario = {
      id: crypto.randomUUID(),
      role: "user",
      content: input,
    }

    setMensagens((prev) => [...prev, mensagemUsuario])
    setInput("")
    setCarregando(true)

    try {
      const response = await axios.post(`${API_URL}/api/chat/`, {
        mensagem: input,
        session_id: SESSION_ID,
      })

      const mensagemBot = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.data?.resposta ?? "Não consegui gerar uma resposta. Tente novamente.",
      }

      setMensagens((prev) => [...prev, mensagemBot])

    } catch (erro) {
      setMensagens((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: "Erro ao conectar com o servidor. Tente novamente.",
        },
      ])
    } finally {
      setCarregando(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      enviarMensagem()
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl flex flex-col h-[90vh] bg-gray-900 rounded-2xl shadow-2xl overflow-hidden">

        {/* header */}
        <div className="bg-gray-800 px-6 py-4 border-b border-gray-700">
          <h1 className="text-white font-bold text-lg">LifeNavigator AI</h1>
          <p className="text-gray-400 text-sm">Análises de concurso público e custo de vida em SP</p>
        </div>

        {/* mensagens */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {mensagens.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white rounded-br-sm"
                    : "bg-gray-700 text-gray-100 rounded-bl-sm"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}

          {carregando && (
            <div className="flex justify-start">
              <div className="bg-gray-700 text-gray-400 rounded-2xl rounded-bl-sm px-4 py-3 text-sm">
                Analisando...
              </div>
            </div>
          )}

          {/* ancora pro auto-scroll */}
          <div ref={fimDaListaRef} />
        </div>

        {/* input */}
        <div className="px-4 py-4 border-t border-gray-700 flex gap-3">
          <textarea
            className="flex-1 bg-gray-800 text-white rounded-xl px-4 py-3 text-sm resize-none outline-none border border-gray-700 focus:border-blue-500 transition-colors disabled:opacity-50"
            rows={1}
            placeholder="Digite sua pergunta..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={carregando}
          />
          <button
            onClick={enviarMensagem}
            disabled={carregando || !input.trim()}
            aria-label="Enviar mensagem"
            title="Enviar mensagem"
            className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 rounded-xl transition-colors"
          >
            →
          </button>
        </div>

      </div>
    </div>
  )
}