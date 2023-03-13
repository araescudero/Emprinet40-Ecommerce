def insertar_usuario(username,password):
    query=f""" 
    INSERT INTO usuario(username,password)
    values
    ('{username}','{password}')
    """
    return query