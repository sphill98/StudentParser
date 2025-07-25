from student_parser import create_app

app = create_app()

if __name__ == '__main__':
    # app.config에서 PORT 값을 가져와 사용
    app.run(host='0.0.0.0', debug=True, port=app.config['PORT'])
