from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def hello():
    return jsonify({"message": "Hello, World!"})

@app.route("/weather/<city>")
def weather(city):
    return jsonify({"city": city, "temp": 28})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    return jsonify({"received": data, "reply": "AI 回复"})

if __name__ == "__main__":
    print("Server is running on port 8000")
    app.run(port=8000, debug=True)
    
    
# # main.py
# from fastapi import FastAPI
# from pydantic import BaseModel

# app = FastAPI()

# class WeatherRequest(BaseModel):
#     city: str

# @app.get("/")
# def read_root():
#     return {"message": "Hello, World!"}

# @app.get("/weather/{city}")
# def get_weather(city: str):
#     return {"city": city, "temp": 28, "condition": "sunny"}

# @app.post("/chat")
# def chat(req: WeatherRequest):
#     return {"city": req.city, "message": f"{req.city} 今天天气晴，28 度"}