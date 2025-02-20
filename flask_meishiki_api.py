from flask import Flask, request, jsonify
from converter import date_converter, time_converter
from meishiki import Meishiki

app = Flask(__name__)

@app.route("/get_gogyo", methods=["POST"])
def get_gogyo():
    """API endpoint to calculate the Five Elements (五行)."""
    
    try:
        data = request.get_json()
        
        # Extract parameters from JSON
        birthday_text = data.get("birthday", "")
        time_text = data.get("time", "")
        sex = data.get("sex", 0)  # Default: Male (0), Female (1)

        # Convert date & time
        date = date_converter(birthday_text)
        birthday, t_flag = time_converter(date, time_text)

        # Run Meishiki calculation
        meishiki = Meishiki(birthday, t_flag, sex)
        meishiki.build_meishiki()

        # Extract Five Elements (五行) distribution
        gogyo_result = meishiki.meishiki.get("gogyo", {})

        # Return only 五行 data
        return jsonify({
            "五行": {
                "木": gogyo_result[0],
                "火": gogyo_result[1],
                "土": gogyo_result[2],
                "金": gogyo_result[3],
                "水": gogyo_result[4]
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
