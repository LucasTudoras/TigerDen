def colleges_dict():
    colleges = {
        '1967': "Butler College",
        '1976': "Butler College",
        'Bloomberg': "Butler College",
        'Bogle': "Butler College",
        'Scully': "Butler College",
        'Wilf': "Butler College",
        'Yoseloff': "Butler College",
        '99Alexander': "Forbes College",
        'Annex': "Forbes College",
        'Main': "Forbes College",
        'Blair': "Mathey College",
        'Campbell': "Mathey College",
        'Edwards': "Mathey College",
        'Joline': "Mathey College",
        'Little': "Mathey College",
        'Hamilton': "Mathey College",
        'Addy': "New College West",
        'Jose E. Feliciano': "New College West",
        'Aliya Kanji': "New College West",
        'Kwanza Jones': "New College West",
        'Buyers': "Rockefeller College",
        'Campbell': "Rockefeller College",
        'Holder': "Rockefeller College",
        'Witherspoon': "Rockefeller College",
        '1901': "Upperclass",
        'Feinberg': "Upperclass",
        'Patton': "Upperclass",
        '1903': "Upperclass",
        'Foulke': "Upperclass",
        'Pyne': "Upperclass",
        'Brown': "Upperclass",
        'Henry': "Upperclass",
        'Scully': "Upperclass",
        'Cuyler': "Upperclass",
        'Laughlin': "Upperclass",
        'Spelman': "Upperclass",
        'Dickinson Street, 2': "Upperclass",
        'Little': "Upperclass",
        'Walker': "Upperclass",
        'Dod': "Upperclass",
        'Lockhart': "Upperclass",
        'Wright': "Upperclass",
        '1981': "Whitman College",
        'Baker E': "Whitman College",
        'Baker S': "Whitman College",
        'Fisher': "Whitman College",
        'Hargadon': "Whitman College",
        'Lauritzen': "Whitman College",
        'Murley': "Whitman College",
        'Wendell B': "Whitman College",
        'Wendell C': "Whitman College",
        'Fu': "Yeh College",
        'Grousbeck': "Yeh College",
        'Hariri': "Yeh College",
        'Mannion': "Yeh College",
    }
    
    return colleges

def halls_dict():
    halls = {
        '1967': "Butler College",
        '1976': "Butler College",
        'Bloomberg': "Butler College",
        'Bogle': "Butler College",
        'Scully': "Butler College",
        'Wilf': "Butler College",
        'Yoseloff': "Butler College",
        '99Alexander': "Forbes College",
        'Annex': "Forbes College",
        'Main': "Forbes College",
        'Blair': "Mathey College",
        'Campbell-Mathey': "Mathey College",
        'Edwards': "Mathey College",
        'Joline': "Mathey College",
        'Little-Mathey': "Mathey College",
        'Hamilton': "Mathey College", 
        'Addy': "New College West",
        'Jose Feliciano': "New College West",
        'Aliya Kanji': "New College West",
        'Kwanza Jones': "New College West",
        'Buyers': "Rockefeller College",
        'Campbell-Rocky': "Rockefeller College",
        'Holder': "Rockefeller College",
        'Witherspoon': "Rockefeller College",
        '1901': "Upperclass",
        'Feinberg': "Upperclass",
        'Patton': "Upperclass",
        '1903': "Upperclass",
        'Foulke': "Upperclass",
        'Pyne': "Upperclass",
        'Brown': "Upperclass",
        'Henry': "Upperclass",
        'Scully': "Upperclass",
        'Cuyler': "Upperclass",
        'Laughlin': "Upperclass",
        'Spelman': "Upperclass",
        'Dickinson Street, 2': "Upperclass",
        'Little-Upperclass': "Upperclass",
        'Walker': "Upperclass",
        'Dod': "Upperclass",
        'Lockhart': "Upperclass",
        'Wright': "Upperclass",
        '1981': "Whitman College",
        'Baker': "Whitman College",
        'Fisher': "Whitman College",
        'Hargadon': "Whitman College",
        'Lauritzen': "Whitman College",
        'Murley': "Whitman College",
        'Wendell': "Whitman College",
        'Fu': "Yeh College",
        'Grousbeck': "Yeh College",
        'Hariri': "Yeh College",
        'Mannion': "Yeh College",
    }

    return halls

def check_halls(college):
    halls = []

    if college == 'Butler College':
        halls = ['1967', '1976', 'Bloomberg', 'Bogle', 'Scully', 'Wilf', 'Yoseloff']

    elif college == 'Forbes College':
        halls = ['99Alexander', 'Annex', 'Main']

    elif college == 'Mathey College':
        halls = ['Blair', 'Campbell', 'Edwards', 'Hamilton', 'Joline', 'Little']
        
    elif college == 'New College West':
        halls = ['Addy', 'Jose E. Feliciano', 'Kanji', 'Kwanza Jones']
    
    elif college == 'Rockefeller College':
        halls = ['Buyers', 'Campbell', 'Holder', 'Witherspoon']

    elif college == 'Upperclass':
        halls = ['1901', 'Feinberg','Patton', '1903', 'Foulke', 'Pyne', 'Brown', 'Henry', 'Scully', 'Cuyler', 'Laughlin', 'Spelman', 'Dickinson Street, 2', 'Little', 'Walker', 'Dod', 'Lockhart', 'Wright']

    elif college == 'Whitman College':
        halls = ['1981', 'Baker E', 'Baker S', 'Fisher', 'Hargadon', 'Lauritzen', 'Murley', 'Wendell B', 'Wendell C']
    
    elif college == 'Yeh College':
        halls = ['Fu', 'Grousbeck', 'Hariri', 'Mannion']
    
    return halls