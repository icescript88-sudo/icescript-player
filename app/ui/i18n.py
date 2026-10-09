"""
Internationalization (i18n) module for Icescript Player.
Supports Portuguese (pt) and English (en) with live language switching.
"""
from typing import Dict

STRINGS: Dict[str, Dict[str, str]] = {
    "pt": {
        # General / Brand
        "app_tag": "PLAYER",
        "slogan": "Mais que cursos, é o teu futuro!",
        "offline_vault": "COFRE OFFLINE • 100% PRIVADO",
        
        # Navigation
        "nav_featured": "DESTAQUES",
        "nav_courses": "CURSOS",
        "nav_continue": "CONTINUAR",
        "nav_about": "ℹ️ SOBRE",
        "nav_protect": "🔒 PROTEGER",
        "nav_scan_tooltip": "Escanear pasta de vídeos",
        "skin_hbo": "🎨 TEMA: HBO",
        "skin_editorial": "🎨 TEMA: POSTER",
        "lang_btn": "🌐 PT",

        # Showcase / Hero
        "select_course": "Selecione um Curso",
        "hero_default_desc": "Reprodução de vídeo privada, acelerada por hardware e protegida com criptografia local AES-256.",
        "badge_protected": "🔒 PROTEGIDO AES-256",
        "badge_ready": "PRONTO P/ ASSISTIR",
        "badge_completed": "CONCLUÍDO",
        "watch_lesson": "▶  ASSISTIR AULA",
        "watch_now": "▶  ASSISTIR AGORA",
        "all_lessons": "TODAS AS AULAS",
        "prev_lesson": "Aula Anterior",
        "next_lesson": "Próxima Aula",
        "lesson_counter": "Aula {current} de {total} em {course}.",
        "no_courses_title": "Nenhum Curso Encontrado",
        "no_courses_desc": "Adicione pastas de vídeos ou arquivos .cvid na pasta 'videos/' e clique em 🔄 Escanear.",
        "no_lessons": "Nenhuma aula encontrada nesta pasta.",

        # Editorial Skin
        "index_title": "ÍNDICE",
        "kicker_default": "CURSO",
        "footer_vault": "─── Cofre Offline",

        # Browser
        "browser_title": "📚 Biblioteca de Cursos",
        "browser_back": "← Voltar ao Início",
        "courses_label": "CURSOS",
        "lessons_label": "AULAS",
        "materials_label": "MATERIAIS / PDF",
        "view_pdf": "📄 ABRIR PDF",
        "no_materials": "Nenhum material PDF nesta pasta.",
        "continue_none": "Nenhuma aula pendente encontrada no histórico.",
        "continue_dialog_title": "Continuar Assistindo",

        # Player & VLC Controls
        "player_browser_btn": "←  PAINEL",
        "ready_to_play": "Pronto para reproduzir",
        "seek_back_tooltip": "Voltar 10s (Seta Esquerda)",
        "seek_fwd_tooltip": "Avançar 10s (Seta Direita)",
        "play_pause_tooltip": "Reproduzir / Pausar (Espaço)",
        "speed_tooltip": "Velocidade de Reprodução",
        "fullscreen_tooltip": "Tela Cheia (F / F11)",
        "vlc_play": "Reproduzir (Espaço)",
        "vlc_pause": "Pausar (Espaço)",
        "vlc_prev": "Faixa Anterior (P)",
        "vlc_stop": "Parar (S)",
        "vlc_next": "Próxima Faixa (N)",
        "vlc_fullscreen": "Alternar Tela Cheia (F / F11)",
        "vlc_playlist": "Alternar Lista de Reprodução (Ctrl+L)",
        "vlc_effects": "Ajustes e Efeitos (Ctrl+E)",
        "vlc_repeat_off": "Repetir: Desativado",
        "vlc_repeat_all": "Repetir: Todas as Aulas",
        "vlc_repeat_one": "Repetir: Aula Atual",
        "vlc_shuffle_on": "Ordem Aleatória: Ativada",
        "vlc_shuffle_off": "Ordem Aleatória: Desativada",
        "vlc_mute": "Silenciar / Desilenciar (M)",
        "vlc_speed": "Velocidade de Reprodução",
        "vlc_time_tooltip": "Clique para alternar Tempo Total / Tempo Restante",
        "vlc_playlist_title": "LISTA DE REPRODUÇÃO",
        "vlc_filter_placeholder": "🔍 Filtrar aulas do curso…",
        "vlc_effects_title": "Ajustes e Efeitos — Estilo VLC",
        "vlc_tab_audio": "Áudio",
        "vlc_tab_video": "Vídeo",
        "vlc_tab_playback": "Reprodução",
        "vlc_volume_booster": "Amplificação de Volume (Booster até 125%)",
        "vlc_aspect_ratio": "Proporção de Tela (Aspect Ratio)",
        "vlc_aspect_auto": "Original / Automático",
        "vlc_aspect_16_9": "16:9 Widescreen",
        "vlc_aspect_4_3": "4:3 Clássico",
        "vlc_aspect_fill": "Preencher Janela",

        # Login / Auth
        "login_create_title": "Crie o seu PIN (mínimo 4 caracteres)",
        "login_enter_title": "Digite o seu PIN para continuar",
        "login_pin_placeholder": "Digite o PIN…",
        "login_confirm_placeholder": "Confirme o PIN…",
        "login_create_btn": "Criar PIN",
        "login_unlock_btn": "Desbloquear",
        "login_err_short": "O PIN deve ter no mínimo 4 caracteres.",
        "login_err_mismatch": "Os PINs não coincidem. Tente novamente.",
        "login_err_empty": "Por favor, digite o seu PIN.",
        "login_err_wrong": "PIN incorreto.",
        "login_err_failed": "Falha ao definir o PIN.",

        # Protection Dialog & Instructor Security
        "protect_title": "Proteger & Criptografar Vídeos",
        "protect_header": "🔒 Criptografar Vídeos de Cursos",
        "protect_desc": "Converte vídeos brutos (.mp4, .mkv, etc.) no formato protegido .cvid.\nVídeos criptografados só podem ser abertos dentro do Icescript Player.",
        "protect_select_file": "📄 Selecionar Arquivo...",
        "protect_find_all": "📁 Buscar Não Criptografados em 'videos/'",
        "protect_delete_check": "Excluir vídeo(s) original(is) após criptografia",
        "protect_start_btn": "🔒 Iniciar Criptografia",
        "protect_close_btn": "Fechar",
        "protect_no_files": "Nenhum arquivo selecionado.",
        "admin_auth_title": "Acesso Restrito ao Instrutor",
        "admin_auth_header": "🔒 Senha Mestre de Instrutor",
        "admin_auth_desc": "Esta área é reservada para o produtor/instrutor criptografar aulas.\nDigite a senha mestre de administrador para continuar:",
        "admin_pw_placeholder": "Digite a Senha Mestre…",
        "admin_unlock_btn": "Desbloquear",
        "admin_cancel_btn": "Cancelar",
        "admin_err_wrong": "Senha de instrutor incorreta.",
        "admin_err_empty": "Por favor, digite a senha mestre.",
        "admin_change_pw_btn": "🔑 Alterar Senha Mestre",
        "admin_new_pw_title": "Alterar Senha Mestre",
        "admin_new_pw_prompt": "Digite a nova senha mestre (mínimo 4 caracteres):",
        "admin_pw_changed": "Senha mestre de instrutor atualizada com sucesso!",
        "protect_none_found": "Todos os vídeos na pasta 'videos/' já estão criptografados!",
        "protect_done_title": "Proteção Concluída",
        "protect_done_msg": "{count} vídeo(s) criptografados com sucesso para o formato protegido .cvid.",

        # Activation / License
        "act_window_title": "Ativação de Licença - Icescript Player",
        "act_header": "Ativação do Computador",
        "act_sub": "Envie o ID deste computador ao instrutor para receber sua Chave de Ativação.",
        "act_dev_id_label": "ID DESTE COMPUTADOR:",
        "act_copy_btn": "📋 Copiar ID",
        "act_copied": "Copiado!",
        "act_key_label": "CHAVE DE ATIVAÇÃO:",
        "act_key_placeholder": "Insira a chave (ex: ACT-XXXX-XXXX-XXXX-XXXX)…",
        "act_submit_btn": "Ativar Licença",
        "act_err_invalid": "Chave de ativação inválida para este computador.",
        "act_err_empty": "Por favor, insira a chave de ativação.",
        "act_success": "Computador ativado com sucesso!",

        # Notes & Certificate
        "notes_btn": "📝 ANOTAÇÕES",
        "notes_title": "Anotações da Aula",
        "notes_add_placeholder": "Escreva uma anotação neste momento do vídeo...",
        "notes_save_btn": "Salvar Nota",
        "notes_empty": "Nenhuma anotação salva para esta aula ainda.",
        "cert_btn": "🎓 CERTIFICADO",
        "cert_title": "Certificado de Conclusão",
        "cert_generate_btn": "🎓 Emitir Certificado PDF",
        "cert_congrats": "Parabéns! Você completou 100% deste curso.",
        "cert_not_ready": "Você precisa assistir 100% de todas as aulas deste curso para desbloquear o certificado.",
        "cert_saved_msg": "Certificado gerado com sucesso e salvo em:",
    },

    "en": {
        # General / Brand
        "app_tag": "PLAYER",
        "slogan": "More than courses, it's your future!",
        "offline_vault": "OFFLINE VAULT • 100% PRIVATE",

        # Navigation
        "nav_featured": "FEATURED",
        "nav_courses": "COURSES",
        "nav_continue": "CONTINUE",
        "nav_about": "ℹ️ ABOUT",
        "nav_protect": "🔒 PROTECT",
        "nav_scan_tooltip": "Scan videos folder",
        "skin_hbo": "🎨 SKIN: HBO",
        "skin_editorial": "🎨 SKIN: POSTER",
        "lang_btn": "🌐 EN",

        # Showcase / Hero
        "select_course": "Select a Course",
        "hero_default_desc": "Experience zero-buffer, hardware-accelerated private video playback protected with local AES-256 encryption.",
        "badge_protected": "🔒 AES-256 PROTECTED",
        "badge_ready": "READY TO WATCH",
        "badge_completed": "COMPLETED",
        "watch_lesson": "▶  WATCH LESSON",
        "watch_now": "▶  WATCH NOW",
        "all_lessons": "ALL LESSONS",
        "prev_lesson": "Previous Lesson",
        "next_lesson": "Next Lesson",
        "lesson_counter": "Lesson {current} of {total} in {course}.",
        "no_courses_title": "No Courses Found",
        "no_courses_desc": "Add video folders or .cvid files into the 'videos/' directory, then click 🔄 Scan.",
        "no_lessons": "No lessons found in this course folder.",

        # Editorial Skin
        "index_title": "INDEX",
        "kicker_default": "COURSE",
        "footer_vault": "─── Offline Vault",

        # Browser
        "browser_title": "📚 Course Library",
        "browser_back": "← Back to Showcase",
        "courses_label": "COURSES",
        "lessons_label": "LESSONS",
        "materials_label": "MATERIALS / PDF",
        "view_pdf": "📄 OPEN PDF",
        "no_materials": "No PDF materials in this course.",
        "continue_none": "No unfinished lessons found in your history.",
        "continue_dialog_title": "Continue Watching",

        # Player & VLC Controls
        "player_browser_btn": "←  BROWSER",
        "ready_to_play": "Ready to play",
        "seek_back_tooltip": "Seek Backward 10s (Left Arrow)",
        "seek_fwd_tooltip": "Seek Forward 10s (Right Arrow)",
        "play_pause_tooltip": "Play / Pause (Space)",
        "speed_tooltip": "Playback Speed",
        "fullscreen_tooltip": "Fullscreen (F / F11)",
        "vlc_play": "Play (Space)",
        "vlc_pause": "Pause (Space)",
        "vlc_prev": "Previous Track (P)",
        "vlc_stop": "Stop (S)",
        "vlc_next": "Next Track (N)",
        "vlc_fullscreen": "Toggle Fullscreen (F / F11)",
        "vlc_playlist": "Toggle Playlist (Ctrl+L)",
        "vlc_effects": "Extended Settings & Effects (Ctrl+E)",
        "vlc_repeat_off": "Repeat: Off",
        "vlc_repeat_all": "Repeat: All Lessons",
        "vlc_repeat_one": "Repeat: Current Lesson",
        "vlc_shuffle_on": "Random / Shuffle: On",
        "vlc_shuffle_off": "Random / Shuffle: Off",
        "vlc_mute": "Mute / Unmute (M)",
        "vlc_speed": "Playback Speed",
        "vlc_time_tooltip": "Click to toggle Total / Remaining Time",
        "vlc_playlist_title": "PLAYLIST",
        "vlc_filter_placeholder": "🔍 Filter course lessons…",
        "vlc_effects_title": "Adjustments and Effects — VLC Style",
        "vlc_tab_audio": "Audio",
        "vlc_tab_video": "Video",
        "vlc_tab_playback": "Playback",
        "vlc_volume_booster": "Volume Booster (up to 125%)",
        "vlc_aspect_ratio": "Aspect Ratio",
        "vlc_aspect_auto": "Original / Default",
        "vlc_aspect_16_9": "16:9 Widescreen",
        "vlc_aspect_4_3": "4:3 Classic",
        "vlc_aspect_fill": "Fill Window",

        # Login / Auth
        "login_create_title": "Create your PIN (min 4 characters)",
        "login_enter_title": "Enter your PIN to continue",
        "login_pin_placeholder": "Enter PIN…",
        "login_confirm_placeholder": "Confirm PIN…",
        "login_create_btn": "Create PIN",
        "login_unlock_btn": "Unlock",
        "login_err_short": "PIN must be at least 4 characters.",
        "login_err_mismatch": "PINs do not match. Try again.",
        "login_err_empty": "Please enter your PIN.",
        "login_err_wrong": "Incorrect PIN.",
        "login_err_failed": "Failed to set PIN.",

        # Protection Dialog & Instructor Security
        "protect_title": "Protect & Encrypt Videos",
        "protect_header": "🔒 Encrypt Course Videos",
        "protect_desc": "Convert raw video files (.mp4, .mkv, etc.) into protected .cvid format.\nEncrypted videos can only be played inside Icescript Player.",
        "protect_select_file": "📄 Select File...",
        "protect_find_all": "📁 Find All Unencrypted in 'videos/'",
        "protect_delete_check": "Delete original raw video(s) after encryption",
        "protect_start_btn": "🔒 Start Encryption",
        "protect_close_btn": "Close",
        "protect_no_files": "No files selected.",
        "admin_auth_title": "Instructor Access Required",
        "admin_auth_header": "🔒 Instructor Master Password",
        "admin_auth_desc": "This area is restricted to the course creator/instructor.\nEnter master password to continue:",
        "admin_pw_placeholder": "Enter Master Password…",
        "admin_unlock_btn": "Unlock",
        "admin_cancel_btn": "Cancel",
        "admin_err_wrong": "Incorrect instructor password.",
        "admin_err_empty": "Please enter the master password.",
        "admin_change_pw_btn": "🔑 Change Master Password",
        "admin_new_pw_title": "Change Master Password",
        "admin_new_pw_prompt": "Enter new master password (min 4 characters):",
        "admin_pw_changed": "Instructor master password updated successfully!",
        "protect_none_found": "All videos in the videos/ folder are already encrypted!",
        "protect_done_title": "Protection Complete",
        "protect_done_msg": "{count} video(s) successfully encrypted into protected .cvid format.",

        # Activation / License
        "act_window_title": "License Activation - Icescript Player",
        "act_header": "Computer Activation",
        "act_sub": "Send this Computer ID to your instructor to receive your Activation Key.",
        "act_dev_id_label": "THIS COMPUTER ID:",
        "act_copy_btn": "📋 Copy ID",
        "act_copied": "Copied!",
        "act_key_label": "ACTIVATION KEY:",
        "act_key_placeholder": "Enter key (e.g. ACT-XXXX-XXXX-XXXX-XXXX)…",
        "act_submit_btn": "Activate License",
        "act_err_invalid": "Invalid activation key for this computer.",
        "act_err_empty": "Please enter the activation key.",
        "act_success": "Computer activated successfully!",

        # Notes & Certificate
        "notes_btn": "📝 NOTES",
        "notes_title": "Lesson Notes",
        "notes_add_placeholder": "Write a note at this video timestamp...",
        "notes_save_btn": "Save Note",
        "notes_empty": "No notes saved for this lesson yet.",
        "cert_btn": "🎓 CERTIFICATE",
        "cert_title": "Completion Certificate",
        "cert_generate_btn": "🎓 Generate PDF Certificate",
        "cert_congrats": "Congratulations! You have completed 100% of this course.",
        "cert_not_ready": "You need to watch 100% of all lessons to unlock your certificate.",
        "cert_saved_msg": "Certificate generated successfully and saved at:",
    },
}


class I18n:
    """Translation manager singleton."""
    _current_lang = "pt"  # Default to Portuguese

    @classmethod
    def get_lang(cls) -> str:
        return cls._current_lang

    @classmethod
    def set_lang(cls, lang: str):
        if lang in STRINGS:
            cls._current_lang = lang

    @classmethod
    def t(cls, key: str, **kwargs) -> str:
        lang_dict = STRINGS.get(cls._current_lang, STRINGS["en"])
        val = lang_dict.get(key, STRINGS["en"].get(key, key))
        if kwargs:
            try:
                return val.format(**kwargs)
            except Exception:
                return val
        return val


def t(key: str, **kwargs) -> str:
    """Convenience global translation function."""
    return I18n.t(key, **kwargs)
