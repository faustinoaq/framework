from balboa import get

with get('/frank-says') as r:
    def res():
        pass
    r.execute(res)
    r.text('Put this in your pipe & smoke it!')

@get('/frank-says')
def frank_says():
    return 'Put this in your pipe & smoke it!'
