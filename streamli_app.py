"""
FlashBriefs Streamlit Application
================================

This Streamlit app replicates the FlashBriefs concept in a single file. It
allows users to select their preferred language, region and topics, load
condensed news summaries and chat with an agent for additional context.

Because external API access may be limited on some hosting platforms, the app
uses a small built‑in sample dataset. In a production environment you can
replace the `fetch_news` function with calls to an actual news API (e.g.
NewsAPI.org, RSS feeds or your own backend). The agent chat also suggests
related articles from the loaded items.
"""

import streamlit as st
from datetime import datetime


# Define a small sample dataset for demonstration purposes. Each item
# represents a news summary with metadata. The `topics` field is a list of
# keywords indicating the category of the article.
SAMPLE_ITEMS = [
    {
        "title": "Apple dévoile son nouveau casque de réalité mixte",
        "summary": "Apple a présenté un casque de réalité mixte qui combine réalité augmentée et réalité virtuelle.",
        "source": "Le Monde",
        "link": "https://www.lemonde.fr/tech/article/2025/08/18/apple-casque-realite-mixte.html",
        "lang": "fr",
        "country": "fr",
        "topics": ["tech"]
    },
    {
        "title": "La France adopte une loi sur la neutralité carbone",
        "summary": "Le parlement français a voté une loi visant la neutralité carbone d'ici 2050.",
        "source": "AFP",
        "link": "https://www.afp.com/fr/neutralite-carbone-france-2050",
        "lang": "fr",
        "country": "fr",
        "topics": ["environnement", "politique"]
    },
    {
        "title": "Une avancée majeure dans la lutte contre le cancer du sein",
        "summary": "Des chercheurs ont développé un traitement prometteur contre certaines formes de cancer du sein.",
        "source": "France24",
        "link": "https://www.france24.com/fr/sante/avancee-cancer-sein",
        "lang": "fr",
        "country": "fr",
        "topics": ["health", "science"]
    },
    {
        "title": "Tesla annonce une nouvelle batterie révolutionnaire",
        "summary": "Tesla affirme avoir développé une batterie capable de faire 1 000 km avec une seule charge.",
        "source": "Reuters",
        "link": "https://www.reuters.com/business/autos-transportation/tesla-new-battery-1000km-range",
        "lang": "en",
        "country": "int",
        "topics": ["tech", "economy"]
    },
    {
        "title": "Climate change threatens global food security",
        "summary": "Scientists warn that rising temperatures could reduce crop yields by up to 25% by 2050.",
        "source": "CNN",
        "link": "https://www.cnn.com/2025/08/18/climate-food-security-study",
        "lang": "en",
        "country": "int",
        "topics": ["environnement", "science"]
    },
    {
        "title": "Blockchain technology transforms supply chains",
        "summary": "Companies are using blockchain to improve transparency and reduce costs in supply chain management.",
        "source": "Bloomberg",
        "link": "https://www.bloomberg.com/news/articles/2025-08-17/blockchain-supply-chain",
        "lang": "en",
        "country": "int",
        "topics": ["tech", "economy"]
    },
    {
        "title": "Une découverte exoplanétaire bouleverse l'astronomie",
        "summary": "Une exoplanète de la taille de la Terre a été découverte dans la zone habitable d'une étoile proche.",
        "source": "Cité des Sciences",
        "link": "https://www.cite-sciences.fr/exoplanete-zone-habitable",
        "lang": "fr",
        "country": "fr",
        "topics": ["science"]
    },
    {
        "title": "Global markets rally as inflation cools",
        "summary": "Stock markets worldwide have surged after reports showed that inflation is slowing down.",
        "source": "Financial Times",
        "link": "https://www.ft.com/content/markets-rally-inflation-cools",
        "lang": "en",
        "country": "int",
        "topics": ["economy"]
    },
]


def fetch_news(lang: str, country: str, selected_topics: list[str]) -> list[dict]:
    """Filter the SAMPLE_ITEMS based on language, country and topics.

    Args:
        lang: 'fr' or 'en'.
        country: 'fr', 'int' or 'both'.
        selected_topics: list of topic strings.

    Returns:
        A list of news items matching the criteria. If no items match, returns an empty list.
    """
    results = []
    for item in SAMPLE_ITEMS:
        # Filter by language
        if lang and item['lang'] != lang:
            continue
        # Filter by country
        if country != 'both' and item['country'] != country:
            continue
        # Filter by topics
        if selected_topics:
            if not any(topic in item['topics'] for topic in selected_topics):
                continue
        results.append(item)
    return results


def find_related_articles(article: dict, all_items: list[dict], max_count: int = 3) -> list[str]:
    """Find titles of other articles sharing at least one topic with the current article.

    Args:
        article: The current article dictionary.
        all_items: List of all available articles.
        max_count: Number of related titles to return.

    Returns:
        A list of up to `max_count` article titles.
    """
    related = []
    for item in all_items:
        if item is article:
            continue
        # Check for overlap in topics
        if set(item['topics']).intersection(article['topics']):
            related.append(item['title'])
        if len(related) >= max_count:
            break
    return related


def generate_agent_response(user_query: str, article: dict, all_items: list[dict]) -> str:
    """Generate a simple agent response based on the user query.

    The agent currently does not interpret the query; it only suggests other
    articles on similar topics. In a production system, this function could
    leverage an AI service (e.g. OpenAI API) to provide deeper context and
    answer user questions.

    Args:
        user_query: The text of the user's question.
        article: The current article.
        all_items: All available articles.

    Returns:
        A response string.
    """
    related_titles = find_related_articles(article, all_items)
    if related_titles:
        suggestions = ' ; '.join(f'« {title} »' for title in related_titles)
        return f"Voici d'autres articles qui pourraient vous intéresser : {suggestions}."
    return "Je n'ai pas trouvé d'autres articles pertinents pour le moment."


def main():
    st.set_page_config(page_title="FlashBriefs", layout="wide")
    st.title("FlashBriefs – L'essentiel en 1 minute")

    # Initialize session state variables
    if 'news' not in st.session_state:
        st.session_state['news'] = []
    if 'chat_messages' not in st.session_state:
        st.session_state['chat_messages'] = {}
    if 'chat_open' not in st.session_state:
        st.session_state['chat_open'] = None  # Index of the article whose chat is open

    # Sidebar controls
    st.sidebar.header("Préférences")
    lang = st.sidebar.selectbox("Langue", options=["fr", "en"], format_func=lambda x: "Français" if x == "fr" else "English")
    country = st.sidebar.selectbox(
        "Zone",
        options=["both", "fr", "int"],
        format_func=lambda x: "National et International" if x == "both" else ("France" if x == "fr" else "International"),
    )
    topic_options = {
        "tech": "Tech",
        "science": "Science",
        "economy": "Économie",
        "environnement": "Environnement",
        "health": "Santé",
    }
    selected_topics = st.sidebar.multiselect("Sujets", options=list(topic_options.keys()), format_func=lambda x: topic_options[x])

    if st.sidebar.button("Charger les brèves"):
        st.session_state['news'] = fetch_news(lang, country, selected_topics)
        st.session_state['chat_open'] = None
        st.session_state['chat_messages'] = {}

    # Display news cards
    if st.session_state['news']:
        for idx, item in enumerate(st.session_state['news']):
            with st.container():
                st.subheader(item['title'])
                st.write(item['summary'])
                st.caption(f"Source : {item['source']}")
                # Link to full article
                st.markdown(f"[Lire la suite]({item['link']})")
                # Agent button
                if st.button("Agent Flashbriefs", key=f"agent-btn-{idx}"):
                    st.session_state['chat_open'] = idx
                    # Initialize chat messages list for this article if not present
                    if idx not in st.session_state['chat_messages']:
                        st.session_state['chat_messages'][idx] = []

                # Chat modal if this article's chat is open
                if st.session_state['chat_open'] == idx:
                    with st.expander("Discussion avec l'agent", expanded=True):
                        st.write(f"**{item['title']}**")
                        st.write(item['summary'])
                        # Display messages
                        messages = st.session_state['chat_messages'][idx]
                        for m in messages:
                            if m['role'] == 'user':
                                st.markdown(f"<div style='text-align:right;color:var(--color-primary);'><strong>Vous :</strong> {m['content']}</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div style='text-align:left;color:var(--color-secondary);'><strong>Agent :</strong> {m['content']}</div>", unsafe_allow_html=True)
                        # Input field
                        user_input = st.text_input(
                            "Posez votre question",
                            value="",
                            key=f"input-{idx}",
                            placeholder="Demandez plus de détails…",
                        )
                        if st.button("Envoyer", key=f"send-btn-{idx}") and user_input:
                            # Append user message
                            st.session_state['chat_messages'][idx].append({
                                'role': 'user',
                                'content': user_input,
                            })
                            # Generate agent response
                            reply = generate_agent_response(user_input, item, st.session_state['news'])
                            st.session_state['chat_messages'][idx].append({
                                'role': 'agent',
                                'content': reply,
                            })

    # Footer
    st.markdown("---")
    st.caption(
        "Les brèves sont mises à jour à 07 h et 18 h 30 (Fuseau Europe/Paris).\n"
        "Version freemium : résumés avec publicité. Version premium : sans publicité et accès approfondi."
    )


if __name__ == "__main__":
    main()
