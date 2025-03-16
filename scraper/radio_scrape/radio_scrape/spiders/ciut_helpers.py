def show_name(response) -> str:

    # Usually the show title is in the H1 tag
    if response.xpath("//h1/text()").get():
        name = response.xpath("//h1/text()").get()
    else:
        # if no H1 tag, then let's try the title tag
        name = response.xpath("//title/text()").get().split(" - ")[0]

    return name
