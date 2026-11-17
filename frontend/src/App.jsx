import { useState } from 'react'
import './App.css'
import Detector from './Detector'

export default function App() {
  const [residentes, setResidentes] = useState([])
  const [id, setId] = useState('')
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState('')
  const [consultado, setConsultado] = useState(false)

  async function consultar(idBuscado = '') {
    setCargando(true)
    setError('')
    setResidentes([])
    setConsultado(false)

    try {
      const ruta = idBuscado
        ? '/api/residentes/' + encodeURIComponent(idBuscado)
        : '/api/residentes'

      const respuesta = await fetch(ruta)

      if (respuesta.status === 404) {
        throw new Error('Residente no encontrado')
      }

      if (!respuesta.ok) {
        throw new Error('La API no pudo completar la consulta')
      }

      const datos = await respuesta.json()
      setResidentes(Array.isArray(datos) ? datos : [datos])
      setConsultado(true)
    } catch (err) {
      setError(
        err instanceof TypeError
          ? 'No se pudo conectar con la API'
          : err.message
      )
    } finally {
      setCargando(false)
    }
  }

  function buscar(evento) {
    evento.preventDefault()
    consultar(id)
  }

  return (
    <main>
      <h1>SmartBuilding</h1>
      <p>Consulta de residentes</p>

      <button
        onClick={() => consultar()}
        disabled={cargando}
      >
        Ver todos
      </button>

      <form onSubmit={buscar}>
        <label htmlFor="residente-id">ID del residente</label>
        <input
          id="residente-id"
          type="number"
          min="1"
          step="1"
          required
          value={id}
          onChange={(evento) => setId(evento.target.value)}
        />
        <button type="submit" disabled={cargando}>
          Buscar
        </button>
      </form>

      {cargando && <p role="status">Consultando...</p>}
      {error && <p role="alert">{error}</p>}

      {consultado && residentes.length === 0 && (
        <p>No hay residentes registrados.</p>
      )}

      {residentes.length > 0 && (
        <table>
          <caption>Resultados de la consulta</caption>
          <thead>
            <tr>
              <th scope="col">ID</th>
              <th scope="col">Nombre</th>
              <th scope="col">Torre</th>
              <th scope="col">Apartamento</th>
            </tr>
          </thead>
          <tbody>
            {residentes.map((residente) => (
              <tr key={residente.id}>
                <td>{residente.id}</td>
                <td>{residente.full_name}</td>
                <td>{residente.tower}</td>
                <td>{residente.apartment}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
	<Detector />
    </main>
  )
}
