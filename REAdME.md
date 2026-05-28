#  This is a simple basic app for reciepts and payements

New Features Summary
Feature	Tab	What It Does
➕ Add Product	     📦 Manage	Enter name, price, stock → saves to database
✏️ Edit Product   	📦 Manage	Select product → edit fields → update in database
🗑️ Delete Product	 📦 Manage	Select product → confirm → permanently removed
🔍 Filter Products	📦 Manage	Live search/filter in management table
Click to Fill Form	 📦 Manage	Click any product row → form auto-fills
🔄 Clear Form	       📦 Manage	Reset all form fields
📋 Receipt History	 📋 History	View all past receipts sorted newest first
🧾 Receipt Detail	   📋 History	Click a receipt → see full formatted receipt
🔍 Search History	   📋 History	Filter by receipt number, date, or payment type
🗑️ Delete Receipt	  📋 History	Remove a receipt from history permanently
📊 Summary Bar	     📋 History	Shows total receipts, total sales, cash vs card count


Sale Items Saved	Auto	Every item in every sale stored in sale_items table
Tab Navigation	All	Tabs auto-refresh data when switched
Duplicate Check	📦 Manage	Prevents adding products with same name
Validation	    📦 Manage	Checks for valid name, price, and stock values
Status Messages	📦 Manage	Green confirmation messages that auto-clear
