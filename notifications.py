import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import Config

# ─── EMAIL ─────────────────────────────────────────────────────────────────────

def envoyer_email(sujet, corps_html, corps_texte=None):
    """Envoie un email de notification à l'équipe Loge Facile Niger."""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = sujet
        msg['From']    = Config.MAIL_DEFAULT_SENDER
        msg['To']      = Config.MAIL_RECEIVER

        if corps_texte:
            msg.attach(MIMEText(corps_texte, 'plain', 'utf-8'))
        msg.attach(MIMEText(corps_html, 'html', 'utf-8'))

        with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            server.sendmail(Config.MAIL_DEFAULT_SENDER, Config.MAIL_RECEIVER, msg.as_string())

        print(f"[EMAIL] Envoye : {sujet}")
        return True

    except Exception as e:
        print(f"[EMAIL] Erreur : {e}")
        return False


def notifier_nouvelle_demande(data):
    """Email pour une nouvelle demande de logement (locataire)."""
    sujet = f"[Loge Facile] Nouvelle demande de {data.get('nom', 'N/A')}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;border:1px solid #e0e0e0;border-radius:12px;overflow:hidden;">
      <div style="background:linear-gradient(135deg,#1A3A6B,#2A5298);padding:28px 32px;">
        <h1 style="color:#fff;margin:0;font-size:1.4rem;">&#127968; Nouvelle Demande de Logement</h1>
        <p style="color:rgba(255,255,255,0.7);margin:6px 0 0;font-size:0.9rem;">Loge Facile Niger &mdash; Notification automatique</p>
      </div>
      <div style="padding:28px 32px;background:#f9fafb;">
        <table style="width:100%;border-collapse:collapse;">
          <tr><td style="padding:8px 0;color:#666;font-size:0.85rem;width:140px;">Nom complet</td><td style="padding:8px 0;font-weight:600;color:#0D1B3E;">{data.get('nom','—')}</td></tr>
          <tr style="background:#fff;"><td style="padding:8px 12px;color:#666;font-size:0.85rem;">Telephone</td><td style="padding:8px 12px;font-weight:600;color:#F47C20;">{data.get('telephone','—')}</td></tr>
          <tr><td style="padding:8px 0;color:#666;font-size:0.85rem;">Email</td><td style="padding:8px 0;color:#0D1B3E;">{data.get('email','—')}</td></tr>
          <tr style="background:#fff;"><td style="padding:8px 12px;color:#666;font-size:0.85rem;">Type logement</td><td style="padding:8px 12px;color:#0D1B3E;">{data.get('type_logement','—')}</td></tr>
          <tr><td style="padding:8px 0;color:#666;font-size:0.85rem;">Budget</td><td style="padding:8px 0;color:#0D1B3E;">{data.get('budget','—')}</td></tr>
          <tr style="background:#fff;"><td style="padding:8px 12px;color:#666;font-size:0.85rem;">Quartier</td><td style="padding:8px 12px;color:#0D1B3E;">{data.get('quartier','—')}</td></tr>
          <tr><td style="padding:8px 0;color:#666;font-size:0.85rem;vertical-align:top;">Precisions</td><td style="padding:8px 0;color:#0D1B3E;">{data.get('precisions','—')}</td></tr>
        </table>
      </div>
      <div style="padding:16px 32px;background:#0D1B3E;text-align:center;">
        <p style="color:rgba(255,255,255,0.5);font-size:0.78rem;margin:0;">Loge Facile Niger &bull; +227 97 43 16 19 &bull; logefacile.niger@gmail.com</p>
      </div>
    </div>
    """
    return envoyer_email(sujet, html)


def notifier_nouvelle_proposition(data, fichiers=None):
    """Email pour une nouvelle proposition de logement (proprietaire)."""
    sujet = f"[Loge Facile] Nouvelle proposition de {data.get('nom', 'N/A')}"
    nb_fichiers = len(fichiers) if fichiers else 0
    fichiers_html = f'<tr style="background:#fff;"><td style="padding:8px 12px;color:#666;font-size:0.85rem;">Fichiers joints</td><td style="padding:8px 12px;color:#2A5298;font-weight:600;">{nb_fichiers} fichier(s) uploade(s)</td></tr>' if nb_fichiers else ''

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;border:1px solid #e0e0e0;border-radius:12px;overflow:hidden;">
      <div style="background:linear-gradient(135deg,#F47C20,#D4600A);padding:28px 32px;">
        <h1 style="color:#fff;margin:0;font-size:1.4rem;">&#127968; Nouvelle Proposition de Logement</h1>
        <p style="color:rgba(255,255,255,0.8);margin:6px 0 0;font-size:0.9rem;">Un proprietaire soumet son bien &mdash; a verifier et publier</p>
      </div>
      <div style="padding:28px 32px;background:#f9fafb;">
        <table style="width:100%;border-collapse:collapse;">
          <tr><td style="padding:8px 0;color:#666;font-size:0.85rem;width:140px;">Nom complet</td><td style="padding:8px 0;font-weight:600;color:#0D1B3E;">{data.get('nom','—')}</td></tr>
          <tr style="background:#fff;"><td style="padding:8px 12px;color:#666;font-size:0.85rem;">Telephone</td><td style="padding:8px 12px;font-weight:600;color:#F47C20;">{data.get('telephone','—')}</td></tr>
          <tr><td style="padding:8px 0;color:#666;font-size:0.85rem;">Type logement</td><td style="padding:8px 0;color:#0D1B3E;">{data.get('type_logement','—')}</td></tr>
          <tr style="background:#fff;"><td style="padding:8px 12px;color:#666;font-size:0.85rem;">Quartier</td><td style="padding:8px 12px;color:#0D1B3E;">{data.get('quartier','—')}</td></tr>
          <tr><td style="padding:8px 0;color:#666;font-size:0.85rem;">Loyer mensuel</td><td style="padding:8px 0;font-weight:600;color:#0D1B3E;">{data.get('loyer','—')} FCFA</td></tr>
          <tr style="background:#fff;"><td style="padding:8px 12px;color:#666;font-size:0.85rem;vertical-align:top;">Description</td><td style="padding:8px 12px;color:#0D1B3E;">{data.get('description','—')}</td></tr>
          {fichiers_html}
        </table>
      </div>
      <div style="padding:20px 32px;background:#fff8f3;border-top:1px solid #ffe0cc;">
        <p style="color:#D4600A;font-size:0.85rem;margin:0;">&#9888;&#65039; Connectez-vous au panneau admin pour examiner cette proposition et la publier.</p>
      </div>
      <div style="padding:16px 32px;background:#0D1B3E;text-align:center;">
        <p style="color:rgba(255,255,255,0.5);font-size:0.78rem;margin:0;">Loge Facile Niger &bull; +227 97 43 16 19 &bull; logefacile.niger@gmail.com</p>
      </div>
    </div>
    """
    return envoyer_email(sujet, html)


# ─── WHATSAPP (TWILIO) ──────────────────────────────────────────────────────────

def notifier_whatsapp_demande(data):
    """Envoie une notification WhatsApp via Twilio pour une demande locataire."""
    if not Config.TWILIO_SID or not Config.TWILIO_AUTH_TOKEN:
        print("[WHATSAPP] Twilio non configure, notification ignoree.")
        return False
    try:
        from twilio.rest import Client
        client = Client(Config.TWILIO_SID, Config.TWILIO_AUTH_TOKEN)
        message = (
            f"*[Loge Facile] Nouvelle demande*\n\n"
            f"*Nom :* {data.get('nom','—')}\n"
            f"*Tel :* {data.get('telephone','—')}\n"
            f"*Type :* {data.get('type_logement','—')}\n"
            f"*Budget :* {data.get('budget','—')}\n"
            f"*Quartier :* {data.get('quartier','—')}"
        )
        client.messages.create(
            body=message,
            from_=Config.TWILIO_WHATSAPP_FROM,
            to=Config.TWILIO_WHATSAPP_TO
        )
        print("[WHATSAPP] Notification demande envoyee.")
        return True
    except Exception as e:
        print(f"[WHATSAPP] Erreur : {e}")
        return False


def notifier_whatsapp_proposition(data, nb_fichiers=0):
    """Envoie une notification WhatsApp via Twilio pour une proposition proprietaire."""
    if not Config.TWILIO_SID or not Config.TWILIO_AUTH_TOKEN:
        print("[WHATSAPP] Twilio non configure, notification ignoree.")
        return False
    try:
        from twilio.rest import Client
        client = Client(Config.TWILIO_SID, Config.TWILIO_AUTH_TOKEN)
        fichiers_txt = f"\n*Fichiers :* {nb_fichiers} joint(s)" if nb_fichiers else ""
        message = (
            f"*[Loge Facile] Nouvelle proposition*\n\n"
            f"*Nom :* {data.get('nom','—')}\n"
            f"*Tel :* {data.get('telephone','—')}\n"
            f"*Type :* {data.get('type_logement','—')}\n"
            f"*Quartier :* {data.get('quartier','—')}\n"
            f"*Loyer :* {data.get('loyer','—')} FCFA"
            f"{fichiers_txt}\n\n"
            f"_Connectez-vous au panneau admin pour examiner._"
        )
        client.messages.create(
            body=message,
            from_=Config.TWILIO_WHATSAPP_FROM,
            to=Config.TWILIO_WHATSAPP_TO
        )
        print("[WHATSAPP] Notification proposition envoyee.")
        return True
    except Exception as e:
        print(f"[WHATSAPP] Erreur : {e}")
        return False
