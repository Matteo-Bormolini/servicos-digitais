from servicosdigitais.app import criar_app

app = criar_app()
print("MIGRATE IN APP?" , hasattr(app, 'extensions') and 'migrate' in app.extensions)
print("SQLALCHEMY_DATABASE_URI =", app.config.get("SQLALCHEMY_DATABASE_URI"))
print("app.instance_path =", app.instance_path)

if __name__ == "__main__":
    app.run(debug=True)
