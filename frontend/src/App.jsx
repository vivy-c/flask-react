import { useState } from 'react'
import './App.css'

function App() {
  const [contacts, setContacts] = useState([])

  const fetchContacts = async () => {
    const response = await fetch('http://localhost:5000/contacts')
    const data = await response.json()
    setContacts(data.contacts)
    console.log(data.contacts)
  }
  return (
    <>
      
    </>
  )
}

export default App
