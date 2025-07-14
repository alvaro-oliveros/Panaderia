document.getElementById("form-sede").addEventListener("submit", async function(e) {
  e.preventDefault();
  const nombre = document.getElementById("nombre").value;
  const direccion = document.getElementById("direccion").value;
  const usuario_id = document.getElementById("usuario_id").value;

  const response = await fetch(`${API_URL}/sedes/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ Nombre: nombre, Direccion: direccion, Usuario_id: parseInt(usuario_id) })
  });

  if (response.ok) {
    alert("Sede creada correctamente");
    location.reload();
  } else {
    alert("Error al crear sede");
  }
});

async function cargarSedes() {
  const res = await fetch(`${API_URL}/sedes`);
  const sedes = await res.json();
  const lista = document.getElementById("lista-sedes");
  lista.innerHTML = "";
  sedes.forEach(s => {
    const li = document.createElement("li");
    li.textContent = `ID: ${s.idSedes}, Nombre: ${s.Nombre}, Dirección: ${s.Direccion}`;
    lista.appendChild(li);
  });
}

cargarSedes();
