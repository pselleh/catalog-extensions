def paginate(items, page, page_size):
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size

    return {
        "count": total,
        "page": page,
        "pageSize": page_size,
        "results": items[start:end],
    }
