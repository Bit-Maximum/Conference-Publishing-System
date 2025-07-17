def get_characters_count(doc):
    """
    Calculates the total character count of a document.

    Parameters:
        doc (Document): The document object containing paragraphs.

    Returns:
        int: The total number of characters in the document.
    """
    return sum(len(p.text) for p in doc.paragraphs)
