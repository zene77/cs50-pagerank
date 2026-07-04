import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    pages = list(corpus.keys())
    n = len(pages)
    links = corpus[page]

    # Si la página no tiene enlaces → repartir entre todas
    if len(links) == 0:
        return {p: 1 / n for p in pages}

    # Probabilidad base (random jump)
    base = (1 - damping_factor) / n

    # Probabilidad de seguir un enlace
    link_prob = damping_factor / len(links)

    probs = {}
    for p in pages:
        if p in links:
            probs[p] = base + link_prob
        else:
            probs[p] = base

    return probs


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus.keys())
    counts = {p: 0 for p in pages}

    # Empezar en una página aleatoria
    current = random.choice(pages)

    for _ in range(n):
        counts[current] += 1
        model = transition_model(corpus, current, damping_factor)
        current = random.choices(
            population=list(model.keys()),
            weights=list(model.values())
        )[0]

    # Normalizar
    return {p: counts[p] / n for p in pages}


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus.keys())
    n = len(pages)

    # Inicializar PR
    pr = {p: 1 / n for p in pages}

    converged = False
    while not converged:
        new_pr = {}

        for p in pages:
            total = 0
            for q in pages:
                if p in corpus[q]:
                    total += pr[q] / len(corpus[q])
                if len(corpus[q]) == 0:
                    total += pr[q] / n

            new_pr[p] = (1 - damping_factor) / n + damping_factor * total

        # Comprobar convergencia
        converged = all(abs(new_pr[p] - pr[p]) < 0.001 for p in pages)
        pr = new_pr

    return pr


if __name__ == "__main__":
    main()
