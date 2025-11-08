// ----------------------------
// 🚪 LOGOUT - Botão Funcional
// ----------------------------
const logoutBtn = document.getElementById('logout-btn');
if (logoutBtn) {
  logoutBtn.addEventListener('click', function(e) {
    e.preventDefault();
    
    // Confirmação antes de sair
    if (confirm('Tem certeza que deseja sair do sistema?')) {
      // Redireciona para a rota de logout do Flask
      window.location.href = '/logout';
    }
  });
}

// ----------------------------
// 🎨 Gráficos e Contadores (Dados via API)
// ----------------------------
async function carregarDadosDashboard() {
    try {
        const response = await fetch('/api/graficos');
        const data = await response.json();
        
        // Atualizar contadores (se necessário, embora o Flask já faça isso no HTML)
        // document.getElementById("clienteCount").textContent = data.clientes_count;
        // document.getElementById("produtoCount").textContent = data.produtos_count;
        document.getElementById("vendaCount").textContent = `R$ ${data.vendas_total.toFixed(2)}`;

        // Criar Gráficos
        criarGraficos(data);

    } catch (error) {
        console.error("Erro ao carregar dados do dashboard:", error);
    }
}

function criarGraficos(data) {
  // 1. Gráfico de Vendas (Barra)
  const ctxVendas = document.getElementById("salesChart");
  new Chart(ctxVendas, {
    type: "bar",
    data: {
      labels: data.vendas_mensais.labels,
      datasets: [{
        label: "Vendas (R$)",
        data: data.vendas_mensais.data,
        backgroundColor: "#3498db"
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });

  // 2. Gráfico de Crescimento de Clientes (Linha)
  const ctxClientes = document.getElementById("clientesChart");
  new Chart(ctxClientes, {
    type: "line",
    data: {
      labels: data.clientes_crescimento.labels,
      datasets: [{
        label: "Novos Clientes",
        data: data.clientes_crescimento.data,
        borderColor: "#2ecc71",
        borderWidth: 2,
        fill: false
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });

  // 3. Gráfico de Vendas por Canal (Pizza)
  const ctxVendasMensais = document.getElementById("vendasMensais");
  new Chart(ctxVendasMensais, {
    type: "pie",
    data: {
      labels: data.vendas_canais.labels,
      datasets: [{
        data: data.vendas_canais.data,
        backgroundColor: ["#3498db", "#2ecc71", "#f1c40f"]
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
}

// ----------------------------
// 🌓 Alternar Tema
// ----------------------------
const themeToggle = document.getElementById("theme-toggle");
const icon = themeToggle.querySelector("i");
const body = document.body;

function aplicarTema() {
  const temaSalvo = localStorage.getItem("theme");
  if (temaSalvo === "dark") {
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
// 🚀 Inicialização
// ----------------------------
window.addEventListener("DOMContentLoaded", () => {
  carregarDadosDashboard();
});