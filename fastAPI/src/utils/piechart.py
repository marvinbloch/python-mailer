from typing import List

from ..config.config import PIECHART_FILE_PATH

from ..models.models import Email
from ..services.crud import get_all_emails, get_histories_by_email_id
import matplotlib.pyplot as plt

async def create_piechart(db):    
    emails: List[Email] = await get_all_emails(db)

    not_valid = 0
    not_reachable = 0
    not_send = 0
    not_clicked = 0
    clicked = 0

    for email in emails:
        if not email.valid:
            not_valid += 1
        elif not email.reachable:
            not_reachable += 1
        else:
            histories = await get_histories_by_email_id(db, email.id)
            email_attempts = len(histories)
            email_clicks = sum(history.click_count for history in histories)

            if email_attempts == 0:
                not_send += 1
            elif email_clicks == 0:
                not_clicked += 1
            else:
                clicked += 1

    labels = []
    sizes = []
    colors = []
    explode = []

    if not_reachable > 0:
        labels.append('Not Reachable')
        sizes.append(not_reachable)
        colors.append('#ff9999')
        explode.append(0.1)
    
    if not_valid > 0:
        labels.append('Not Valid')
        sizes.append(not_valid)
        colors.append('#ff99cc')
        explode.append(0)
    
    if not_send > 0:
        labels.append('Not Sent')
        sizes.append(not_send)
        colors.append('#ffcc99')
        explode.append(0)
    
    if not_clicked > 0:
        labels.append('Not Clicked')
        sizes.append(not_clicked)
        colors.append('#66b3ff')
        explode.append(0)
    
    if clicked > 0:
        labels.append('Clicked')
        sizes.append(clicked)
        colors.append('#99ff99')
        explode.append(0)
    
    fig, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
           shadow=True, startangle=90)
    ax.axis('equal')  
   
    fig.savefig(PIECHART_FILE_PATH)