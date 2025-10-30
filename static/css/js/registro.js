// Validação em tempo real do formulário de registro
document.addEventListener('DOMContentLoaded', function() {
  const form = document.querySelector('.register-form');
  const nomeInput = document.getElementById('nome');
  const senhaInput = document.getElementById('senha');
  const confirmarSenhaInput = document.getElementById('confirmar_senha');
  const registerBtn = document.getElementById('register-btn');

  // Validar nome de usuário
  nomeInput.addEventListener('input', function() {
    const value = this.value.trim();
    const isValid = value.length >= 3 && /^[a-zA-Z0-9_]+$/.test(value);
    
    updateValidation(this, isValid);
  });

  // Validar senha
  senhaInput.addEventListener('input', function() {
    const value = this.value;
    const isValid = value.length >= 4;
    
    updateValidation(this, isValid);
    updatePasswordStrength(value);
    validatePasswordMatch();
  });

  // Validar confirmação de senha
  confirmarSenhaInput.addEventListener('input', function() {
    validatePasswordMatch();
  });

  // Atualizar força da senha
  function updatePasswordStrength(password) {
    const strengthBar = document.querySelector('.strength-progress');
    const strengthText = document.querySelector('.strength-text');
    
    let strength = 0;
    let color = '#ef4444';
    let text = 'Fraca';
    
    if (password.length >= 4) strength += 25;
    if (password.length >= 6) strength += 25;
    if (/[A-Z]/.test(password)) strength += 25;
    if (/[0-9]/.test(password)) strength += 25;
    
    if (strength >= 75) {
      color = '#10b981';
      text = 'Forte';
    } else if (strength >= 50) {
      color = '#f59e0b';
      text = 'Média';
    }
    
    strengthBar.style.width = strength + '%';
    strengthBar.style.background = color;
    strengthText.textContent = text;
  }

  // Validar se as senhas coincidem
  function validatePasswordMatch() {
    const senha = senhaInput.value;
    const confirmarSenha = confirmarSenhaInput.value;
    const isValid = senha === confirmarSenha && senha.length > 0;
    
    updateValidation(confirmarSenhaInput, isValid);
  }

  // Atualizar estado de validação
  function updateValidation(input, isValid) {
    const feedback = input.parentElement.querySelector('.input-feedback');
    const validIcon = feedback.querySelector('.valid-icon');
    const invalidIcon = feedback.querySelector('.invalid-icon');
    
    if (input.value.trim() === '') {
      validIcon.style.display = 'none';
      invalidIcon.style.display = 'none';
      input.style.borderColor = '#e2e8f0';
    } else if (isValid) {
      validIcon.style.display = 'inline';
      invalidIcon.style.display = 'none';
      input.style.borderColor = 'rgba(16, 185, 129, 0.5)';
    } else {
      validIcon.style.display = 'none';
      invalidIcon.style.display = 'inline';
      input.style.borderColor = 'rgba(239, 68, 68, 0.5)';
    }
  }

  // Loading no submit
  form.addEventListener('submit', function(e) {
    const senha = senhaInput.value;
    const confirmarSenha = confirmarSenhaInput.value;
    
    if (senha !== confirmarSenha) {
      e.preventDefault();
      alert('As senhas não coincidem!');
      return;
    }
    
    if (!document.getElementById('terms').checked) {
      e.preventDefault();
      alert('Você deve aceitar os termos de serviço!');
      return;
    }
    
    registerBtn.classList.add('loading');
    registerBtn.disabled = true;
  });
});S