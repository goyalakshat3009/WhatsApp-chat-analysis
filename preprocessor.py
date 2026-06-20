import re
import pandas as pd

def preprocess(data):

    # Handle special WhatsApp spaces
    data = data.replace('\u202f', ' ')

    # Supports:
    # 9/28/25, 1:18 PM -
    # 15/06/26, 9:25 pm -
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s?(?:AM|PM|am|pm)\s-\s'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # If chat format is not supported
    if len(messages) == 0 or len(dates) == 0:
        return pd.DataFrame(columns=['date', 'user', 'message'])

    df = pd.DataFrame({
        'user_message': messages,
        'message_date': dates
    })

    # Remove trailing " - "
    df['message_date'] = df['message_date'].str.replace(
        ' - ',
        '',
        regex=False
    )

    # Convert to datetime
    df['message_date'] = pd.to_datetime(
        df['message_date'],
        errors='coerce'
    )

    df.rename(
        columns={'message_date': 'date'},
        inplace=True
    )

    # Remove invalid dates
    df = df.dropna(subset=['date'])

    # Separate users and messages
    users = []
    messages = []

    for message in df['user_message']:

        entry = re.split(
            r'([\w\W]+?):\s',
            message
        )

        if entry[1:]:
            users.append(entry[1])
            messages.append(entry[2])

        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages

    df.drop(
        columns=['user_message'],
        inplace=True
    )

    # Date features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Period feature for heatmap
    period = []

    for hour in df['hour']:

        if hour == 23:
            period.append("23-00")

        elif hour == 0:
            period.append("00-1")

        else:
            period.append(
                str(hour) + "-" + str(hour + 1)
            )

    df['period'] = period

    return df