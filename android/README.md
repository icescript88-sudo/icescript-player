# 📱 Icescript Player — Android Build Workspace

Esta pasta é dedicada ao desenvolvimento, adaptação e compilação da versão **Android (.apk)** do Icescript Player.

---

## 📂 Estrutura da Pasta

```
android/
├── app/          # Código-fonte adaptado para mobile/Android
├── assets/       # Ícones, logos e recursos gráficos mobile
├── build/        # Artefatos temporários e APKs gerados (.apk)
└── README.md     # Orientações da versão Android
```

---

## 🎯 Objetivos desta Versão

1. **Interface Touch-First**:
   - Layout vertical responsivo adaptado para telas de celular.
   - Navegação por abas inferiores (Bottom Navigation) ou gaveta (Drawer).
   - Controles de reprodução com gestos de toque (volume, brilho, busca).

2. **Gerenciamento de Armazenamento Mobile**:
   - Detecção de mídia nos diretórios do Android (`/storage/emulated/0/Download/Icescript` ou SD card).
   - Sem dependência de registro Windows ou comandos PowerShell.

3. **Segurança & Criptografia Portável**:
   - Reutilização do núcleo seguro de criptografia AES-256 (`vault.py`, `encryption.py`).
   - Identificador de hardware baseado no `ANDROID_ID`.

4. **Instalador Leve (APK)**:
   - APK otimizado (~20-40 MB) para instalação rápida.
   - Cursos carregados sob demanda pelo usuário.
