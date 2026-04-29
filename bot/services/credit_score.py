from typing import Dict, List
from bot.models import SessionLocal
from bot.services.database import get_credit_history, save_credit_score

class CreditScoreService:
    """Credit score module - links to free services + manual tracking"""
    
    FREE_SERVICES = [
        {
            "name": "Credit Karma",
            "url": "https://www.creditkarma.com",
            "desc": "Бесплатный TransUnion & Equifax скоринг"
        },
        {
            "name": "Experian",
            "url": "https://www.experian.com/free-credit-score",
            "desc": "FICO Score 8 бесплатно"
        },
        {
            "name": "AnnualCreditReport.com",
            "url": "https://www.annualcreditreport.com",
            "desc": "Официальный бесплатный отчёт раз в год по закону"
        },
        {
            "name": "Credit Sesame",
            "url": "https://www.creditsesame.com",
            "desc": "Бесплатный VantageScore"
        }
    ]
    
    def get_services_text(self) -> str:
        lines = ["<b>💰 Бесплатные сервисы для проверки Credit Score</b>\n"]
        for i, svc in enumerate(self.FREE_SERVICES, 1):
            lines.append(f"{i}. <a href='{svc['url']}'>{svc['name']}</a>")
            lines.append(f"   {svc['desc']}\n")
        lines.append("<i>Перейдите по ссылке, зарегистрируйтесь и получите свой скоринг.</i>")
        lines.append("<i>Потом вернитесь сюда и введите свой результат — я сохраню историю.</i>")
        return "\n".join(lines)
    
    def interpret_score(self, score: int) -> str:
        if score >= 800:
            return "🟢 Отличный (Exceptional)"
        elif score >= 740:
            return "🟢 Очень хороший (Very Good)"
        elif score >= 670:
            return "🟡 Хороший (Good)"
        elif score >= 580:
            return "🟠 Средний (Fair)"
        else:
            return "🔴 Плохой (Poor)"
    
    def save_user_score(self, user_id: int, score: int, bureau: str, note: str = "") -> None:
        db = next(SessionLocal())
        save_credit_score(db, user_id, score, bureau, note)
    
    def get_history_text(self, user_id: int) -> str:
        db = next(SessionLocal())
        history = get_credit_history(db, user_id)
        
        if not history:
            return "📭 У вас пока нет сохранённых записей.\n\nИспользуйте /credit, чтобы добавить свой скоринг."
        
        lines = ["<b>📋 История вашего Credit Score</b>\n"]
        for entry in history:
            rating = self.interpret_score(entry.score)
            lines.append(f"📅 {entry.created_at.strftime('%Y-%m-%d')}")
            lines.append(f"💯 Скор: <b>{entry.score}</b> — {rating}")
            lines.append(f"🏢 Бюро: {entry.bureau}")
            if entry.note:
                lines.append(f"📝 Заметка: {entry.note}")
            lines.append("")
        
        return "\n".join(lines)

credit_service = CreditScoreService()
