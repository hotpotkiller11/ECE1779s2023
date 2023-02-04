from FrontEnd import webapp as front

if __name__ == "__main__":
    front.debug = True

    front.run(host="127.0.0.1", port=5000)


