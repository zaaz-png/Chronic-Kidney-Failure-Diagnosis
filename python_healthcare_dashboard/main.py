from database import init_db
from frontend import CKDDashboardUI

if __name__ == "__main__":
    init_db()
    app = CKDDashboardUI()
    app.mainloop()