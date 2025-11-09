console.log("✅ dashboard.js carregado com sucesso!");

// ----------------------------
// 🚪 Logout
// ----------------------------
document.getElementById('logout-btn').addEventListener('click', e => {
  e.preventDefault();
  if (confirm("Deseja sair do sistema?")) window.location.href = "/logout";
});

// ----------------------------
// 🌓 Tema Escuro
// ----------------------------
const themeToggle = document.getElementById("theme-toggle");
const icon = themeToggle.querySelector("i");
const body = document.body;

function aplicarTema() {
  const tema = localStorage.getItem("theme");
  if (tema === "dark") {
    body.classList.add("dark-mode");
    icon.classList.replace("fa-moon", "fa-sun");
  }
}
aplicarTema();

themeToggle.addEventListener("click", () => {
  body.classList.toggle("dark-mode");
  const dark = body.classList.contains("dark-mode");
  icon.classList.toggle("fa-moon", !dark);
  icon.classList.toggle("fa-sun", dark);
  localStorage.setItem("theme", dark ? "dark" : "light");
});

// ----------------------------
// 📂 Alternar Seções
// ----------------------------
document.querySelectorAll(".menu-item").forEach(item => {
  item.addEventListener("click", () => {
    document.querySelectorAll(".menu-item").forEach(i => i.classList.remove("active"));
    item.classList.add("active");
    const target = item.dataset.target;
    document.querySelectorAll(".content-section").forEach(sec => sec.classList.remove("active"));
    document.getElementById(target).classList.add("active");
  });
});

// ----------------------------
// 💾 Dados fictícios
// ----------------------------
const clientesFicticios = [
  { nome: "João Silva", email: "joao@email.com", telefone: "9999-9999" },
  { nome: "Maria Oliveira", email: "maria@email.com", telefone: "9888-7777" },
];

const produtosFicticios = [
  { nome: "Teclado Gamer", marca: "Logitech", preco: 250.00, estoque: 10 },
  { nome: "Monitor 27''", marca: "Samsung", preco: 1500.00, estoque: 5 },
];

// Preenche tabelas
function carregarTabelas() {
  const clientesTable = document.getElementById("clientesTable").querySelector("tbody");
  clientesTable.innerHTML = clientesFicticios.map(c => `<tr><td>${c.nome}</td><td>${c.email}</td><td>${c.telefone}</td></tr>`).join("");

  const produtosTable = document.getElementById("produtosTable").querySelector("tbody");
  produtosTable.innerHTML = produtosFicticios.map(p => `<tr><td>${p.nome}</td><td>${p.marca}</td><td>R$ ${p.preco.toFixed(2)}</td><td>${p.estoque}</td></tr>`).join("");
}

// ----------------------------
// ➕ Adicionar Cliente/Produto
// ----------------------------
document.getElementById("clienteForm").addEventListener("submit", e => {
  e.preventDefault();
  const form = e.target;
  clientesFicticios.push({
    nome: form.nome.value,
    email: form.email.value,
    telefone: form.telefone.value
  });
  carregarTabelas();
  form.reset();
});

document.getElementById("produtoForm").addEventListener("submit", e => {
  e.preventDefault();
  const form = e.target;
  produtosFicticios.push({
    nome: form.nome.value,
    marca: form.marca.value,
    preco: parseFloat(form.preco.value),
    estoque: parseInt(form.estoque.value)
  });
  carregarTabelas();
  form.reset();
});

// ----------------------------
// 📊 Gráficos Fictícios
// ----------------------------
function criarGraficos() {
  const ctxVendas = document.getElementById("salesChart");
  new Chart(ctxVendas, {
    type: "bar",
    data: {
      labels: ["Jun", "Jul", "Ago", "Set", "Out", "Nov"],
      datasets: [{
        label: "Vendas (R$)",
        data: [4000, 5200, 6100, 7000, 8800, 10200],
        backgroundColor: "#3498db"
      }]
    }
  });

  const ctxClientes = document.getElementById("clientesChart");
  new Chart(ctxClientes, {
    type: "line",
    data: {
      labels: ["Jun", "Jul", "Ago", "Set", "Out", "Nov"],
      datasets: [{
        label: "Novos Clientes",
        data: [5, 8, 12, 10, 15, 20],
        borderColor: "#2ecc71",
        fill: false
      }]
    }
  });

  const ctxCanais = document.getElementById("vendasCanais");
  new Chart(ctxCanais, {
    type: "pie",
    data: {
      labels: ["Online", "Loja Física", "Parceiros"],
      datasets: [{
        data: [55, 35, 10],
        backgroundColor: ["#3498db", "#f1c40f", "#2ecc71"]
      }]
    }
  });
}

// ----------------------------
// 🚀 Inicialização
// ----------------------------
window.addEventListener("DOMContentLoaded", () => {
  carregarTabelas();
  criarGraficos();
});
