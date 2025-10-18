from database import db
from datetime import date, timedelta

class Member(db.Model):
    __tablename__ = 'member'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False, default=date(1900, 1, 1))
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_token = db.Column(db.String(255), unique=True, nullable=True)
    token_expires_at = db.Column(db.DateTime, nullable=True)
    agent_usage = db.Column(db.Numeric(10, 6), nullable=False, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'email': self.email,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'dateOfBirth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'age': self.age(),
            'verified': self.email_verified,
            'agent_usage': self.agent_usage,
        }
    
    def __repr__(self):
        return f'<Member {self.email}>'

    def age(self):
        """Calculate current age from date of birth"""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def age_last_year(self):
        """Returns the member's age as of this day last year."""
        today = date.today()
        try:
            last_year_date = today.replace(year=today.year - 1)
        except ValueError:
            # Handles Feb 29 on non-leap years
            last_year_date = date(today.year - 1, 2, 28)
        return last_year_date.year - self.date_of_birth.year - (
            (last_year_date.month, last_year_date.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def is_birthday(self):
        today = date.today()
        return (self.date_of_birth.month == today.month and
                self.date_of_birth.day == today.day)

    def birthday_within_last_month(self):
        today = date.today()
        # Construct this year's birthday date
        try:
            birthday_this_year = self.date_of_birth.replace(year=today.year)
        except ValueError:
            # Handles Feb 29 on non-leap years: fallback to Feb 28
            birthday_this_year = date(today.year, 2, 28)
        days_since_birthday = (today - birthday_this_year).days
        # Was birthday less than 30 days ago, but not in the future
        return 0 <= days_since_birthday <= 30