from flask import Flask, request, jsonify, render_template, redirect, session, url_for
import sqlite3
import cv2
from ultralytics import YOLO
from paddleocr import PaddleOCR
from flask import Response
from datetime import datetime

from config import login_required

app = Flask(__name__)

def init_db():
    with sqlite3.connect("parking.db") as conn:
        cursor = conn.cursor()

        # Tạo bảng VehicleType
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS VehicleType (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL
        )
        ''')

        # Tạo bảng PriceConvention
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS PriceConvention (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            VehicleTypeID INTEGER NOT NULL,
            Time TEXT NOT NULL,
            Price REAL NOT NULL,
            TicketType TEXT NOT NULL,
            StartTime TEXT NOT NULL,
            EndTime TEXT NOT NULL,
            FOREIGN KEY (VehicleTypeID) REFERENCES VehicleType(ID)
        )
        ''')

        # Tạo bảng ActualParkingFee với EntryTime và ExitTime kiểu DATETIME
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ActualParkingFee (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            VehicleTypeID INTEGER NOT NULL,
            PlateNumber TEXT NOT NULL,
            EntryTime DATETIME NOT NULL,
            ExitTime DATETIME,
            Status TEXT NOT NULL,
            TotalFee REAL,
            Note TEXT,
            FOREIGN KEY (VehicleTypeID) REFERENCES VehicleType(ID)
        )
        ''')

        # Tạo bảng Account
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Account (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT NOT NULL,
            Password TEXT NOT NULL
        )
        ''')

        print("Database initialized successfully.")




# API POSTMAN POST price_convention
# @app.route('/price_convention', methods=['POST'])
# def add_price_convention():
#     data = request.get_json()
#     vehicle_type_id = data.get('VehicleTypeID')
#     time = data.get('Time')
#     price = data.get('Price')
#     ticket_type = data.get('TicketType')
#     start_time = data.get('StartTime')
#     end_time = data.get('EndTime')
#     with sqlite3.connect("parking.db") as conn:
#         cursor = conn.cursor()
#         cursor.execute('''
#         INSERT INTO PriceConvention (VehicleTypeID, Time, Price, TicketType, StartTime, EndTime)
#         VALUES (?, ?, ?, ?, ?, ?)
#         ''', (vehicle_type_id, time, price, ticket_type, start_time, end_time))
#         conn.commit()
#         return jsonify({"message": "Price convention added successfully."}), 201

@app.route('/price_convention', methods=['POST'])
def add_price_convention():
    try:
        # Lấy dữ liệu từ form
        vehicle_type_id = request.form.get('VehicleTypeID')
        time = request.form.get('Time')
        price = request.form.get('Price')
        ticket_type = request.form.get('TicketType')
        start_time = request.form.get('StartTime')
        end_time = request.form.get('EndTime')

        # Thêm vào database
        with sqlite3.connect("parking.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO PriceConvention (VehicleTypeID, Time, Price, TicketType, StartTime, EndTime)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (vehicle_type_id, time, price, ticket_type, start_time, end_time))
            conn.commit()

        return redirect('/price_convention')  # Chuyển hướng về trang chính
    except Exception as e:
        return render_template('price_convention.html', error=str(e))


# API POSTMAN PUT price_convention
# @app.route('/price_convention/<int:id>', methods=['PUT'])
# def update_price_convention(id):
#     try:
#         data = request.json
#         with sqlite3.connect("parking.db") as conn:
#             cursor = conn.cursor()
#             cursor.execute('''
#                 UPDATE PriceConvention
#                 SET VehicleTypeID = ?, Time = ?, Price = ?, TicketType = ?, StartTime = ?, EndTime = ?
#                 WHERE ID = ?
#             ''', (data['VehicleTypeID'], data['Time'], data['Price'], data['TicketType'], data['StartTime'], data['EndTime'], id))
#             conn.commit()
#         return jsonify({"message": "PriceConvention updated successfully!"}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

# API PUT CỦa price_convention trên HTML
@app.route('/price_convention/update/<int:id>', methods=['POST'])
def update_price_convention(id):
    try:
        # Lấy dữ liệu từ form
        vehicle_type_id = request.form.get('VehicleTypeID')
        time = request.form.get('Time')
        price = request.form.get('Price')
        ticket_type = request.form.get('TicketType')
        start_time = request.form.get('StartTime')
        end_time = request.form.get('EndTime')

        # Cập nhật dữ liệu trong database
        with sqlite3.connect("parking.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE PriceConvention
                SET VehicleTypeID = ?, Time = ?, Price = ?, TicketType = ?, StartTime = ?, EndTime = ?
                WHERE ID = ?
            ''', (vehicle_type_id, time, price, ticket_type, start_time, end_time, id))
            conn.commit()

        return redirect('/price_convention')  # Chuyển hướng về trang chính
    except Exception as e:
        return render_template('price_convention.html', error=str(e))


# API POSTMAN của DELETE price_convention
# @app.route('/price_convention/<int:id>', methods=['DELETE'])
# def delete_price_convention(id):
#     try:
#         with sqlite3.connect("parking.db") as conn:
#             cursor = conn.cursor()
#             cursor.execute('DELETE FROM PriceConvention WHERE ID = ?', (id,))
#             conn.commit()
#         return jsonify({"message": "PriceConvention deleted successfully!"}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

@app.route('/price_convention/delete/<int:id>', methods=['POST'])
def delete_price_convention(id):
    try:
        # Xóa dữ liệu trong database
        with sqlite3.connect("parking.db") as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM PriceConvention WHERE ID = ?', (id,))
            conn.commit()

        # Sau khi xóa, lấy lại dữ liệu để render giao diện
        return redirect('/price_convention')  # Chuyển hướng lại trang Price Convention
    except Exception as e:
        # Lấy lại dữ liệu để tránh lỗi giao diện
        with sqlite3.connect("parking.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM PriceConvention')
            rows = cursor.fetchall()
            data = [dict(row) for row in rows]
            total_pages = 1  # Hoặc tính toán lại số trang nếu cần
        return render_template(
            'price_convention.html',
            price_conventions=data,
            current_page=1,
            total_pages=total_pages,
            error=str(e),
            title="Bảng giá vé xe"
        )


# API GET price_convention trên POSTMAN
# @app.route('/price_convention', methods=['GET'])
# def get_all_price_conventions():
#     try:
#         with sqlite3.connect("parking.db") as conn:
#             conn.row_factory = sqlite3.Row
#             cursor = conn.cursor()
#             cursor.execute('SELECT * FROM PriceConvention')
#             rows = cursor.fetchall()
#             data = [dict(row) for row in rows]
#         return jsonify(data), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400



@app.route('/price_convention', methods=['GET'])
@login_required
def get_all_price_conventions():
    try:
        # Lấy trang hiện tại từ query string
        page = request.args.get('page', 1, type=int)
        per_page = 5  # Số lượng bản ghi trên mỗi trang

        # Tính toán bản ghi bắt đầu và kết thúc
        start = (page - 1) * per_page
        end = start + per_page

        # Lấy dữ liệu từ database
        with sqlite3.connect("parking.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT PriceConvention.*, VehicleType.Name AS VehicleTypeName
                FROM PriceConvention
                JOIN VehicleType ON PriceConvention.VehicleTypeID = VehicleType.ID
                ORDER BY VehicleTypeID ASC

            ''')
            rows = cursor.fetchall()
            total_items = len(rows)
            total_pages = (total_items + per_page - 1) // per_page
            data = [dict(row) for row in rows[start:end]]

            # Lấy danh sách VehicleType
            cursor.execute('SELECT ID, Name FROM VehicleType')
            vehicle_types = cursor.fetchall()  # Lấy tất cả (ID, Name)

        # Truyền dữ liệu vào giao diện
        return render_template(
            'price_convention.html',
            price_conventions=data,
            vehicle_types=vehicle_types,
            current_page=page,
            total_pages=total_pages,
            title="Bảng giá vé xe"
        )
    except Exception as e:
        return render_template('price_convention.html', error=str(e), title="Bảng giá vé xe")


## API CHO VEHICALE_TYPE
#API POSTMAN GET VEHICLE_TYPE
# @app.route('/vehicle_type', methods=['GET'])
# def get_all_vehicle_types():
#     try:
#         with sqlite3.connect("parking.db") as conn:
#             conn.row_factory = sqlite3.Row
#             cursor = conn.cursor()
#             cursor.execute('SELECT * FROM VehicleType')
#             rows = cursor.fetchall()
#             data = [dict(row) for row in rows]
#         return jsonify(data), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

#API GET VEHICLE_TYPE HTML
@app.route('/vehicle_type', methods=['GET'])
@login_required
def get_all_vehicle_type():
    try:
        # Lấy trang hiện tại từ query string
        page = request.args.get('page', 1, type=int)
        per_page = 5  # Số lượng bản ghi trên mỗi trang

        # Tính toán bản ghi bắt đầu và kết thúc
        start = (page - 1) * per_page
        end = start + per_page

        # Lấy dữ liệu từ database
        with sqlite3.connect("parking.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM VehicleType')
            rows = cursor.fetchall()
            total_items = len(rows)
            total_pages = (total_items + per_page - 1) // per_page
            data = [dict(row) for row in rows[start:end]]

        # Truyền dữ liệu vào giao diện
        return render_template(
            'vehicle_type.html',
            vehicle_type=data,
            current_page=page,
            total_pages=total_pages,
            title="Quản lý phương tiện"
        )
    except Exception as e:
        return render_template('vehicle_type.html', error=str(e), title="Quản lý phương tiện")


#API POSTMAN POST VEHICLE_TYPE
# @app.route('/vehicle_type', methods=['POST'])
# def add_vehicle_type():
#     data = request.get_json()
#     name = data.get('Name')
#     with sqlite3.connect("parking.db") as conn:
#         cursor = conn.cursor()
#         cursor.execute("INSERT INTO VehicleType (Name) VALUES (?)", (name,))
#         conn.commit()
#         return jsonify({"message": "Vehicle type added successfully."}), 201

#API Post VEHICLE_TYPE html
@app.route('/vehicle_type', methods=['POST'])
def add_vehicle_type():
    try:
        # Lấy dữ liệu từ form
        name = request.form.get('Name')

        # Thêm vào database
        with sqlite3.connect("parking.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO VehicleType (Name)
            VALUES (?)
            ''', (name,))
            conn.commit()
        return redirect('/vehicle_type')  # Chuyển hướng về trang chính
    except Exception as e:
        return render_template('vehicle_type.html', error=str(e))



#API POSTMAN UPDATE VEHICLE_TYPE
# @app.route('/vehicle_type/<int:id>', methods=['PUT'])
# def update_vehicle_type(id):
#     try:
#         data = request.json
#         with sqlite3.connect("parking.db") as conn:
#             cursor = conn.cursor()
#             cursor.execute('''
#                 UPDATE VehicleType
#                 SET Name = ?
#                 WHERE ID = ?
#             ''', (data['Name'], id))
#             conn.commit()
#         return jsonify({"message": "VehicleType updated successfully!"}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

#API UPDATE VEHICLE_TYPE TRÊN HTML
@app.route('/vehicle_type/update/<int:id>', methods=['POST'])
def update_vehicle_type(id):
    try:
        # Lấy dữ liệu từ form
        name = request.form.get('Name')

        # Cập nhật dữ liệu trong database
        with sqlite3.connect("parking.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE VehicleType
                SET Name = ?
                WHERE ID = ?
            ''', (name, id))
            conn.commit()

        return redirect('/vehicle_type')  # Chuyển hướng về trang chính
    except Exception as e:
        return render_template('vehicle_type.html', error=str(e))

#API DELETE VEHICLE_TYPE HTML
@app.route('/vehicle_type/delete/<int:id>', methods=['POST'])
def delete_vehicle_type(id):
    try:
        # Xóa dữ liệu trong database
        with sqlite3.connect("parking.db") as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM VehicleType WHERE ID = ?', (id,))
            conn.commit()

        # Sau khi xóa, lấy lại dữ liệu để render giao diện
        return redirect('/vehicle_type')  # Chuyển hướng lại trang Price Convention
    except Exception as e:
        # Lấy lại dữ liệu để tránh lỗi giao diện
        with sqlite3.connect("parking.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM VehicleType')
            rows = cursor.fetchall()
            data = [dict(row) for row in rows]
            total_pages = 1  # Hoặc tính toán lại số trang nếu cần
        return render_template(
            'vehicle_type.html',
            vehicle_type=data,
            current_page=1,
            total_pages=total_pages,
            error=str(e),
            title="Quản lý phương tiện"
        )

#API POSTMAN DELETE VEHICLE_TYPE
# @app.route('/vehicle_type/<int:id>', methods=['DELETE'])
# def delete_vehicle_type(id):
#     try:
#         with sqlite3.connect("parking.db") as conn:
#             cursor = conn.cursor()
#             cursor.execute('DELETE FROM VehicleType WHERE ID = ?', (id,))
#             conn.commit()
#         return jsonify({"message": "VehicleType deleted successfully!"}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400


##API CHO ACTUAL PARKING FEE

# API POSTMAN CHO POST actual_parking_fee
# @app.route('/actual_parking_fee', methods=['POST'])
# def add_parking_fee():
#     data = request.get_json()
#     vehicle_type_id = data.get('VehicleTypeID')
#     plate_number = data.get('PlateNumber')
#     entry_time = data.get('EntryTime')
#     exit_time = data.get('ExitTime')
#     status = data.get('Status')
#     total_fee = data.get('TotalFee')
#     note = data.get('Note')
#     with sqlite3.connect("parking.db") as conn:
#         cursor = conn.cursor()
#         cursor.execute('''
#         INSERT INTO ActualParkingFee (VehicleTypeID, PlateNumber, EntryTime, ExitTime, Status, TotalFee, Note)
#         VALUES (?, ?, ?, ?, ?, ?, ?)
#         ''', (vehicle_type_id, plate_number, entry_time, exit_time, status, total_fee, note))
#         conn.commit()
#         return jsonify({"message": "Actual parking fee added successfully."}), 201



@app.route('/actual_parking_fee', methods=['POST'])
def add_actual_parking_fee():
    try:
        # Lấy dữ liệu từ form
        vehicle_id = request.form.get('VehicleTypeID')
        plate_number = request.form.get('PlateNumber')
        note = request.form.get('Note')

        # Kết nối đến cơ sở dữ liệu
        with sqlite3.connect("parking.db") as conn:
            cursor = conn.cursor()

            # Kiểm tra xem biển số xe có trạng thái 'Đang gửi xe' trong bảng không
            cursor.execute('''
                SELECT ID, EntryTime FROM ActualParkingFee 
                WHERE PlateNumber = ? AND Status = 'Đang gửi xe'
            ''', (plate_number,))
            record = cursor.fetchone()

            if record:
                # Biển số đã tồn tại trong trạng thái 'Đang gửi xe' -> Cập nhật ExitTime, Status, và TotalCost
                record_id, entry_time = record
                entry_time = datetime.strptime(entry_time, '%Y-%m-%d %H:%M:%S')
                exit_time = datetime.now()
                entry_date = entry_time.date()
                exit_date = exit_time.date()
                duration = exit_date - entry_date

                # Tính toán TotalFee
                total_fee = 0
                if duration.days >= 1:
                    # Trường hợp ExitTime - EntryTime lớn hơn 1 ngày
                    cursor.execute('''
                        SELECT Price FROM PriceConvention
                        WHERE VehicleTypeID = ? AND Time = 'Khuya'
                    ''', (vehicle_id,))
                    row = cursor.fetchone()  # Lưu kết quả truy vấn
                    price = row[0] if row else 0  # Kiểm tra nếu có kết quả, lấy giá trị đầu tiên; nếu không, gán 0
                    total_fee = duration.days * price  # Số ngày tính tròn, kể cả ngày bắt đầu

                else:
                    # Trường hợp ExitTime - EntryTime nhỏ hơn 1 ngày
                    current_time = exit_time.time()  # Lấy thời gian hiện tại (giờ, phút)
                    cursor.execute('''
                        SELECT StartTime, EndTime, Price FROM PriceConvention
                        WHERE VehicleTypeID = ?
                    ''', (vehicle_id,))
                    results = cursor.fetchall()

                    # Duyệt qua các khoảng thời gian trong PriceConvention để tìm thời điểm phù hợp
                    for start_time, end_time, price in results:
                        start_time = datetime.strptime(start_time, '%H:%M:%S').time()
                        end_time = datetime.strptime(end_time, '%H:%M:%S').time()

                        # Kiểm tra ExitTime nằm trong khoảng thời gian
                        if start_time <= current_time <= end_time:
                            total_fee = price
                            break

                # Cập nhật dữ liệu
                cursor.execute('''
                    UPDATE ActualParkingFee
                    SET ExitTime = ?, Status = 'Đã trả xe', TotalFee = ?
                    WHERE ID = ?
                ''', (exit_time.strftime('%Y-%m-%d %H:%M:%S'), total_fee, record_id))

            else:
                # Biển số không tồn tại trong trạng thái 'Đang gửi xe' -> Chèn bản ghi mới
                entry_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                exit_time = None
                status = 'Đang gửi xe'
                total_fee = 0

                cursor.execute('''
                    INSERT INTO ActualParkingFee (VehicleTypeID, PlateNumber, EntryTime, ExitTime, Status, TotalFee, Note)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (vehicle_id, plate_number, entry_time, exit_time, status, total_fee, note))

            # Lưu thay đổi
            conn.commit()

        # Chuyển hướng về trang xử lý hoặc hiển thị thành công
        return redirect('/actual_parking_fee_processing')

    except Exception as e:
        # Trả về trang hiển thị lỗi nếu có vấn đề
        return render_template('actual_parking_fee_processing.html', error=str(e))



# API POSTMAN cho get Actual_parking_fee
# @app.route('/actual_parking_fee', methods=['GET'])
# def get_all_actual_parking_fees():
#     try:
#         with sqlite3.connect("parking.db") as conn:
#             conn.row_factory = sqlite3.Row
#             cursor = conn.cursor()
#             cursor.execute('SELECT * FROM ActualParkingFee')
#             rows = cursor.fetchall()
#             data = [dict(row) for row in rows]
#         return jsonify(data), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

@app.route('/actual_parking_fee', methods=['GET'])
@login_required
def get_all_actual_parking_fee():
    try:
        # Lấy trang hiện tại từ query string
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Số lượng bản ghi trên mỗi trang

        # Tính toán bản ghi bắt đầu và kết thúc
        start = (page - 1) * per_page
        end = start + per_page

        # Lấy dữ liệu từ database
        with sqlite3.connect("parking.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ActualParkingFee.*, VehicleType.Name AS VehicleTypeName
                FROM ActualParkingFee
                JOIN VehicleType ON ActualParkingFee.VehicleTypeID = VehicleType.ID
                ORDER BY ActualParkingFee.EntryTime DESC;
            ''')
            rows = cursor.fetchall()
            total_items = len(rows)
            total_pages = (total_items + per_page - 1) // per_page
            data = [dict(row) for row in rows[start:end]]

        # Truyền dữ liệu vào giao diện
        return render_template(
            'actual_parking_fee.html',
            actual_parking_fee=data,
            current_page=page,
            total_pages=total_pages,
            title="Lịch sử đỗ xe"
        )
    except Exception as e:
        return render_template('actual_parking_fee.html', error=str(e), title="Lịch sử gửi xe")


# API GET DANH SACH ĐANG GỬI XE của ACTUALPARKINGFEE
# @app.route('/actual_parking_fee_processing', methods=['GET'])
# def get_all_actual_parking_fee_processing():
#     try:
#         # Lấy trang hiện tại từ query string
#         page = request.args.get('page', 1, type=int)
#         per_page = 10  # Số lượng bản ghi trên mỗi trang
#
#         # Tính toán bản ghi bắt đầu và kết thúc
#         start = (page - 1) * per_page
#         end = start + per_page
#
#         # Lấy dữ liệu từ database
#         with sqlite3.connect("parking.db") as conn:
#             conn.row_factory = sqlite3.Row
#             cursor = conn.cursor()
#             cursor.execute('''
#                 SELECT ActualParkingFee.*, VehicleType.Name AS VehicleTypeName
#                 FROM ActualParkingFee
#                 JOIN VehicleType ON ActualParkingFee.VehicleTypeID = VehicleType.ID
#                 WHERE ActualParkingFee.Status = 'Đang gửi xe'
#             ''')
#             rows = cursor.fetchall()
#             total_items = len(rows)
#             total_pages = (total_items + per_page - 1) // per_page
#             data = [dict(row) for row in rows[start:end]]
#
#         # Truyền dữ liệu vào giao diện
#         return render_template(
#             'actual_parking_fee_processing.html',
#             actual_parking_fee=data,
#             current_page=page,
#             total_pages=total_pages
#         )
#     except Exception as e:
#         return render_template('actual_parking_fee_processing.html', error=str(e))

@app.route('/actual_parking_fee_processing', methods=['GET'])
@login_required
def get_all_actual_parking_fee_processing():
    try:
        # Lấy trang hiện tại từ query string
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Số lượng bản ghi trên mỗi trang

        # Tính toán bản ghi bắt đầu và kết thúc
        start = (page - 1) * per_page
        end = start + per_page

        with sqlite3.connect("parking.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Lấy danh sách ActualParkingFee
            cursor.execute('''
                SELECT ActualParkingFee.*, VehicleType.Name AS VehicleTypeName
                FROM ActualParkingFee
                JOIN VehicleType ON ActualParkingFee.VehicleTypeID = VehicleType.ID
                WHERE ActualParkingFee.Status = 'Đang gửi xe'
            ''')
            rows = cursor.fetchall()
            total_items = len(rows)
            total_pages = (total_items + per_page - 1) // per_page
            data = [dict(row) for row in rows[start:end]]

            # Lấy danh sách VehicleType
            cursor.execute('SELECT ID, Name FROM VehicleType')
            vehicle_types = cursor.fetchall()  # Lấy tất cả (ID, Name)

        # Truyền dữ liệu vào giao diện
        return render_template(
            'actual_parking_fee_processing.html',
            actual_parking_fee=data,
            vehicle_types=vehicle_types,
            current_page=page,
            total_pages=total_pages,
            title="Quản lý gửi xe"
        )
    except Exception as e:
        return render_template('actual_parking_fee_processing.html', error=str(e), title="Quản lý gửi xe")



# Dùng để lay gia tien ve xe
@app.route('/check_parking_status', methods=['GET'])
@login_required
def check_parking_status():
    try:
        plate_number = request.args.get('plateNumber')
        if not plate_number:
            return jsonify({"error": "Biển số không hợp lệ"}), 400

        with sqlite3.connect("parking.db") as conn:
            cursor = conn.cursor()

            # Kiểm tra trạng thái 'Đang gửi xe'
            cursor.execute('''
                SELECT EntryTime, VehicleTypeID 
                FROM ActualParkingFee 
                WHERE PlateNumber = ? AND Status = 'Đang gửi xe'
            ''', (plate_number,))
            record = cursor.fetchone()

            if record:
                entry_time, vehicle_type_id = record
                entry_time = datetime.strptime(entry_time, '%Y-%m-%d %H:%M:%S')
                exit_time = datetime.now()
                duration = (exit_time - entry_time).days

                total_fee = 0

                if duration >= 1:
                    # Tính phí theo ngày
                    cursor.execute('''
                        SELECT Price FROM PriceConvention
                        WHERE VehicleTypeID = ? AND Time = 'Khuya'
                    ''', (vehicle_type_id,))
                    result = cursor.fetchone()
                    price_per_day = result[0] if result else 0
                    total_fee = duration * price_per_day
                else:
                    # Tính phí theo giờ trong ngày
                    current_time = exit_time.time()
                    cursor.execute('''
                        SELECT StartTime, EndTime, Price FROM PriceConvention
                        WHERE VehicleTypeID = ?
                    ''', (vehicle_type_id,))
                    results = cursor.fetchall()

                    for start_time, end_time, price in results:
                        start_time = datetime.strptime(start_time, '%H:%M:%S').time()
                        end_time = datetime.strptime(end_time, '%H:%M:%S').time()
                        if start_time <= current_time <= end_time:
                            total_fee = price
                            break

                return jsonify({"status": "Đang gửi xe", "price": total_fee})

            return jsonify({"status": "Không tìm thấy xe đang gửi"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# API POSTMAN DELETE actual_parking_fee
# @app.route('/actual_parking_fee/ApiDelete/<int:id>', methods=['DELETE'])
# def APIdelete_actual_parking_fee(id):
#     try:
#         with sqlite3.connect("parking.db") as conn:
#             cursor = conn.cursor()
#             cursor.execute('DELETE FROM ActualParkingFee WHERE ID = ?', (id,))
#             conn.commit()
#         return jsonify({"message": "ActualParkingFee deleted successfully!"}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
#API DELETE CHO HTML




@app.route('/actual_parking_fee/delete/<int:id>', methods=['POST'])
def delete_actual_parking_fee(id):
    try:
        # Xóa dữ liệu trong database
        with sqlite3.connect("parking.db") as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM ActualParkingFee WHERE ID = ?', (id,))
            conn.commit()

        # Sau khi xóa, lấy lại dữ liệu để render giao diện
        return redirect('/actual_parking_fee')  # Chuyển hướng lại trang
    except Exception as e:
        # Lấy lại dữ liệu để tránh lỗi giao diện
        with sqlite3.connect("parking.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM ActualParkingFee')
            rows = cursor.fetchall()
            data = [dict(row) for row in rows]
            total_pages = 1  # Hoặc tính toán lại số trang nếu cần
        return render_template(
            'actual_parking_fee.html',
            actual_parking_fee=data,
            current_page=1,
            total_pages=total_pages,
            error=str(e)
        )

@app.route('/account', methods=['POST'])
def add_account():
    data = request.get_json()
    username = data.get('Username')
    password = data.get('Password')
    with sqlite3.connect("parking.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Account (Username, Password) VALUES (?, ?)", (username, password))
        conn.commit()
        return jsonify({"message": "Account created successfully."}), 201




@app.after_request
def disable_caching(response):
    response.headers['Cache-Control'] = 'no-store'
    return response


yolo_model_path = './modelsYOLO/best.pt'

# Khởi tạo YOLOv8 và PaddleOCR
yolo_model = YOLO(yolo_model_path)
ocr = PaddleOCR(use_angle_cls=True, lang='en')


def detect_license_plate(frame):
    results = yolo_model(frame)  # Phát hiện đối tượng
    if results[0].boxes is None or len(results[0].boxes) == 0:
        return None

    # Lấy vùng biển số (crop)
    for result in results[0].boxes:
        x1, y1, x2, y2 = map(int, result.xyxy[0])
        plate_img = frame[y1:y2, x1:x2]
        return plate_img
    return None


def recognize_text(plate_img):
    # Chuyển ảnh sang định dạng RGB (nếu cần)
    if len(plate_img.shape) == 2 or plate_img.shape[2] != 3:
        plate_img = cv2.cvtColor(plate_img, cv2.COLOR_GRAY2RGB)

    # Nhận dạng ký tự với PaddleOCR
    result = ocr.ocr(plate_img, cls=True)
    if not result or not result[0]:
        return "Không nhận dạng được"

    texts = [line[1][0] for line in result[0]]
    return " ".join(texts)


@app.route('/detect_plate', methods=['POST'])
def detect_plate():
    cap = cv2.VideoCapture(0)  # Mở webcam
    if not cap.isOpened():
        return jsonify({"error": "Không thể mở webcam"}), 500

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return jsonify({"error": "Không thể đọc khung hình"}), 500

    plate_img = detect_license_plate(frame)
    if plate_img is None:
        return jsonify({"error": "Không phát hiện được biển số"}), 404

    recognized_text = recognize_text(plate_img)
    return jsonify({"plate_number": recognized_text})

@app.route('/video_feed')
def video_feed():
    def generate():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            yield b''

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Phát hiện biển số
            results = yolo_model(frame)
            if results[0].boxes is not None and len(results[0].boxes) > 0:
                for result in results[0].boxes:
                    x1, y1, x2, y2 = map(int, result.xyxy[0])  # Lấy tọa độ bounding box
                    plate_img = frame[y1:y2, x1:x2]  # Crop biển số
                    recognized_text = recognize_text(plate_img)  # Nhận dạng văn bản

                    # Vẽ bounding box trên khung hình
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, recognized_text, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Mã hóa khung hình thành JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Trả về khung hình dưới dạng một luồng dữ liệu
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        cap.release()

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


# API ĐĂNG NHẬP
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html',title="Đăng nhập")

# API xử lý đăng nhập
app.secret_key = 'your_secret_key'  # Khóa bí mật cho session

# Route đăng nhập (đã có sẵn trong ứng dụng của bạn)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        with sqlite3.connect("parking.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Account WHERE Username=? AND Password=?", (username, password))
            user = cursor.fetchone()
            if user:
                session['username'] = username  # Lưu trạng thái đăng nhập
                return redirect(url_for('index'))  # Chuyển về trang chủ
            return render_template('login.html', error="Sai tên đăng nhập hoặc mật khẩu!")
    return render_template('login.html')

# API đăng xuất
@app.route('/logout', methods=['POST'])
def logout():
    try:
        session.pop('username', None)  # Xóa session
        return jsonify({"success": True})
    except Exception as e:
        print(f"Lỗi đăng xuất: {e}")
        return jsonify({"success": False})

# Route trang chủ (bảo vệ bằng session)
@app.route('/')
@login_required
def index():
    if 'username' in session:
        return render_template('home.html', title="Trang chủ")
    return redirect(url_for('login'))  # Chuyển hướng nếu chưa đăng nhập

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
