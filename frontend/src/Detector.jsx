

import { useEffect, useRef, useState } from 'react'

export default function Detector() {
  const video = useRef(null)
  const salida = useRef(null)
  const stream = useRef(null)
  const archivo = useRef(null)
  const peticion = useRef(null)
  const sesion = useRef(0)
  const activo = useRef(false)

  const [camaras, setCamaras] = useState([])
  const [camara, setCamara] = useState('')
  const [listo, setListo] = useState(false)
  const [analizando, setAnalizando] = useState(false)
  const [mensaje, setMensaje] = useState('Selecciona un video o abre una camara.')

  useEffect(() => {
    return () => {
      activo.current = false
      sesion.current += 1
      peticion.current?.abort()
      stream.current?.getTracks().forEach((pista) => pista.stop())
      if (archivo.current) URL.revokeObjectURL(archivo.current)
    }
  }, [])

  function detener() {
    activo.current = false
    sesion.current += 1
    peticion.current?.abort()
    stream.current?.getTracks().forEach((pista) => pista.stop())
    stream.current = null

    if (archivo.current) URL.revokeObjectURL(archivo.current)
    archivo.current = null

    video.current.pause()
    video.current.srcObject = null
    video.current.removeAttribute('src')
    video.current.load()

    const canvas = salida.current
    canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height)

    setListo(false)
    setAnalizando(false)
    setMensaje('Detenido.')
  }

  function cargarVideo(evento) {
    const elegido = evento.target.files?.[0]
    if (!elegido) return

    detener()
    archivo.current = URL.createObjectURL(elegido)
    video.current.src = archivo.current
    setMensaje('Video cargado. Pulsa Iniciar deteccion.')
    evento.target.value = ''
  }

  async function abrirCamara() {
    detener()
    const turno = sesion.current
    let nuevoStream

    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        throw new Error('La camara requiere localhost o una conexion HTTPS.')
      }

      nuevoStream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: camara
          ? { deviceId: { exact: camara }, width: { ideal: 640 } }
          : { width: { ideal: 640 } },
      })

      if (turno !== sesion.current) {
        nuevoStream.getTracks().forEach((pista) => pista.stop())
        return
      }

      stream.current = nuevoStream
      video.current.srcObject = nuevoStream
      await video.current.play()

      const dispositivos = await navigator.mediaDevices.enumerateDevices()

      if (turno !== sesion.current) return

      setCamaras(dispositivos.filter((d) => d.kind === 'videoinput'))
      setMensaje('Camara abierta. Pulsa Iniciar deteccion.')
    } catch (error) {
      nuevoStream?.getTracks().forEach((pista) => pista.stop())

      if (turno === sesion.current) {
        detener()
        setMensaje('No se pudo abrir la camara: ' + error.message)
      }
    }
  }

  async function iniciar() {
    if (activo.current || !listo) return

    const turno = sesion.current
    activo.current = true
    setAnalizando(true)
    setMensaje('Iniciando detector...')

    try {
      await video.current.play()

      while (activo.current && turno === sesion.current) {
        const fuente = video.current
        if (fuente.ended) break

        if (fuente.readyState < 2) {
          await new Promise((resolver) => setTimeout(resolver, 200))
          continue
        }

        const captura = document.createElement('canvas')
        const escala = Math.min(1, 640 / fuente.videoWidth)
        captura.width = Math.max(1, Math.round(fuente.videoWidth * escala))
        captura.height = Math.max(1, Math.round(fuente.videoHeight * escala))

        captura.getContext('2d').drawImage(
          fuente, 0, 0, captura.width, captura.height
        )

        const imagen = await new Promise((resolver) => {
          captura.toBlob(resolver, 'image/jpeg', 0.8)
        })

        if (turno !== sesion.current || !activo.current) break
        if (!imagen) throw new Error('No se pudo capturar la imagen.')

        peticion.current = new AbortController()

        const respuesta = await fetch('/api/vision/detectar', {
          method: 'POST',
          headers: { 'Content-Type': 'image/jpeg' },
          body: imagen,
          signal: peticion.current.signal,
        })

        const datos = await respuesta.json()

        if (turno !== sesion.current || !activo.current) break

        if (!respuesta.ok) {
          throw new Error(
            typeof datos.detail === 'string'
              ? datos.detail
              : 'La API no pudo analizar la imagen.'
          )
        }

        const canvas = salida.current
        canvas.width = captura.width
        canvas.height = captura.height

        const dibujo = canvas.getContext('2d')
        dibujo.drawImage(captura, 0, 0)
        dibujo.strokeStyle = '#00ff88'
        dibujo.fillStyle = '#00ff88'
        dibujo.lineWidth = 2
        dibujo.font = '16px sans-serif'

        for (const persona of datos.personas) {
          const [x1, y1, x2, y2] = persona.recuadro
          dibujo.strokeRect(x1, y1, x2 - x1, y2 - y1)
          const textoPersona =
            'Persona ' + Math.round(persona.confianza * 100) + '%'

          const textoColores =
            'Sup: ' + (persona.color_superior || 'No estimable') +
            ' | Inf: ' + (persona.color_inferior || 'No estimable')

          const textoX = Math.max(4, x1)
          const textoY = Math.max(18, y1 - 24)

          dibujo.fillText(textoPersona, textoX, textoY)
          dibujo.fillText(textoColores, textoX, textoY + 20)
	dibujo.fillText(
            'Edad aprox.: ' + (persona.edad_estimada || 'No estimable'),
            textoX,
            textoY + 40
          )
	dibujo.fillText(
            'Prenda sup.: ' + (persona.prenda_superior || 'No estimable'),
            textoX,
            textoY + 60
          )

          dibujo.fillText(
            'Prenda inf.: ' + (persona.prenda_inferior || 'No estimable'),
            textoX,
            textoY + 80
          )
        }

        setMensaje('Personas visibles: ' + datos.total)
        await new Promise((resolver) => setTimeout(resolver, 30))
      }
    } catch (error) {
      if (turno === sesion.current && error.name !== 'AbortError') {
        setMensaje('Error: ' + error.message)
      }
    } finally {
      if (turno === sesion.current) {
        activo.current = false
        setAnalizando(false)
        video.current.pause()
      }
    }
  }

  return (
    <section className="detector">
      <h2>Detector de personas</h2>

      <label>
        Cargar video
        <input type="file" accept="video/*" onChange={cargarVideo} />
      </label>

      <label>
        Camara
        <select value={camara} onChange={(e) => setCamara(e.target.value)}>
          <option value="">Camara predeterminada</option>
          {camaras.map((dispositivo, indice) => (
            <option key={dispositivo.deviceId} value={dispositivo.deviceId}>
              {dispositivo.label || 'Camara ' + (indice + 1)}
            </option>
          ))}
        </select>
      </label>

      <div>
        <button onClick={abrirCamara}>Abrir camara</button>
        <button onClick={iniciar} disabled={!listo || analizando}>
          Iniciar deteccion
        </button>
        <button onClick={detener}>Detener</button>
      </div>

      <p role="status">{mensaje}</p>

      <p>Fuente de video</p>
      <video
        ref={video}
        muted
        playsInline
        onLoadedData={() => setListo(true)}
        onError={() => {
          setListo(false)
          setMensaje('No se pudo reproducir este video.')
        }}
        style={{ width: '100%', maxHeight: 300, background: '#111' }}
      />

      <p>Resultado del detector</p>
      <canvas
        ref={salida}
        style={{ width: '100%', background: '#111' }}
      />
    </section>
  )
}
