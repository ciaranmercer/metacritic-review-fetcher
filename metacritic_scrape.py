import pandas as pd, requests, time, sys, random, unicodedata
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0"}

def title_to_slug(title):
    return title.replace(" ", "-").replace("(", "").replace(")", "").lower()

def remove_accents(director):
    text = unicodedata.normalize('NFD', director)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)

def director_comparison(director_html):
    fetched_director = remove_accents((director_html.find("a", class_="c-crew-list__link").get_text(strip=True)).lower())
    sheet_director = (movie_directors[ind].split(",")[0]).lower()

    if fetched_director != sheet_director:
        return True
    else:
        return False

def handle_request_error(e):
    if isinstance(e, requests.exceptions.ChunkedEncodingError):
        print(f"Connection was ended early, retrying...")
        return 1
    elif isinstance(e, requests.exceptions.HTTPError):
        global ind
        if e.response.status_code == 404:
            print("Movie could not be found, skipping movie...\n")
            ind+= 1
            time.sleep(random.uniform(2, 5))
            return 0
        else:
            print(f"Movie {ind + 1} failed with HTTP error: {e}, halting execution")
            df.to_excel('output.xlsx', index=False)  
            sys.exit(1)

def handle_setup_error(e):
    if isinstance(e, FileNotFoundError):
        print("File was not found. Please ensure the filename is placed in quotations if it contains spaces and that the file exists in the same directory as the script.")    
    elif isinstance(e, ValueError):
        print("Sheet number out of bounds. Sheet indexing starts at 0.")
    elif isinstance(e, IndexError):
        print("Usage: python metacritic_scrape.py <file_name> <sheet_number>")
    
    sys.exit(1)


try:
    spreadsheet = sys.argv[1]
    sheet_number = int(sys.argv[2])
    df = pd.read_excel(spreadsheet, sheet_name=sheet_number, usecols=['Title', 'Year', 'Director'])
    df.insert(3, 'Metacritic', -1)
    movie_titles = df['Title'].to_list()
    movie_years = df['Year'].to_list()
    movie_directors = df['Director'].to_list()
    ind = 0
except (FileNotFoundError, ValueError, IndexError) as err:
    handle_setup_error(err)


for title in movie_titles:
    while True:
        try:
            url = f"https://www.metacritic.com/movie/{title_to_slug(title)}"
            print(f"Trying the URL: {url}")

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() # Checks for non 2XX code, if so throw an error
            soup = BeautifulSoup(response.text, "html.parser")

            director_html = soup.find("div", class_="c-hero-summary__crew-directors")

            if director_comparison(director_html):
                try:
                    print("Original link does not match spreadsheet entry, retrying with year...\n")
                    url = f"https://www.metacritic.com/movie/{title_to_slug(title)}-{int(movie_years[ind])}"
                    print(f"Trying the URL: {url}")

                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")
                except requests.exceptions.HTTPError as err:
                    retry = handle_request_error(err)
                    if retry == 0:
                        break
                    else:
                        time.sleep(random.uniform(2, 5))
                        continue

            score_element = soup.find("div", {"data-testid": "global-score-value-wrapper"})

            score = int(score_element.text.strip())
            print(f"Title: {title} | Score: {score}\n")
            df.at[ind, 'Metacritic'] = score

            ind += 1
            time.sleep(random.uniform(2, 5))
            break
        except requests.exceptions.RequestException as err:
            retry = handle_request_error(err)
            if retry == 0:
                break
            else:
                time.sleep(random.uniform(2, 5))
                continue


print("Score fetching completed! Script ending...")

df.to_excel('output.xlsx', index=False)