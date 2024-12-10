import td
import os

def main():
    port = int(os.environ.get("PORT", 5000))
    td.app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
    main()