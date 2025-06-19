from flask import Blueprint, jsonify, render_template_string, request, make_response, current_app, abort
from src.db.models.users import User
from src.db.core import db
from datetime import datetime

# Create admin blueprint for administrative functions
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def get_all_oauth_users():
    """
    Admin function to retrieve all users who signed up with Google OAuth2
    
    Returns:
        dict: Contains user data and summary statistics
    """
    try:
        # Force refresh database session and query all users
        db.session.expire_all()  # Clear any cached data
        all_users = User.query.all()
        
        print(f"DEBUG: Database query returned {len(all_users)} users")  # Debug log
        
        # Create a list to store user information
        user_data = []
        
        # Loop through each user and extract relevant information
        for user in all_users:
            user_info = {
                'id': user.id,                    # User's unique database ID
                'email': user.email,              # User's email from Google account
                'is_pro': user.is_pro,           # Whether user has pro subscription
                'registration_method': 'Google OAuth2'  # All users use OAuth2
            }
            user_data.append(user_info)
            print(f"DEBUG: Found user {user.id}: {user.email} (Pro: {user.is_pro})")  # Debug log
        
        # Calculate summary statistics
        total_users = len(user_data)
        pro_users = sum(1 for user in user_data if user['is_pro'])
        free_users = total_users - pro_users
        
        print(f"DEBUG: Total users: {total_users}, Pro: {pro_users}, Free: {free_users}")  # Debug log
        
        # Return comprehensive user data with statistics
        return {
            'success': True,
            'total_users': total_users,
            'pro_users': pro_users,
            'free_users': free_users,
            'users': user_data,
            'generated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        # Handle any database or processing errors
        print(f"ERROR in get_all_oauth_users: {e}")  # Debug log
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve user data'
        }



@admin_bp.route('/users')
def view_all_users():
    """
    Admin route to display all OAuth2 users in a web interface
    
    This endpoint provides a simple HTML view of all registered users
    Access: GET /admin/users
    """
    # Get all user data using our admin function
    user_data = get_all_oauth_users()
    
    # Check if data retrieval was successful
    if not user_data['success']:
        return jsonify({
            'error': 'Unable to fetch user data',
            'details': user_data.get('error', 'Unknown error')
        }), 500
      # Enhanced HTML template with debugging information
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin - OAuth2 Users</title>
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            .stats { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 30px; }
            .stats h3 { margin-top: 0; color: white; }
            .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-top: 15px; }
            .stat-item { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px; text-align: center; }
            .stat-number { font-size: 24px; font-weight: bold; }
            .stat-label { font-size: 14px; opacity: 0.9; }
            .controls { margin-bottom: 20px; text-align: center; }
            .refresh-btn { background: #4CAF50; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 16px; margin: 0 10px; }
            .refresh-btn:hover { background: #45a049; }
            .auto-refresh-btn { background: #2196F3; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 16px; margin: 0 10px; }
            .auto-refresh-btn:hover { background: #1976D2; }
            .test-btn { background: #ff9800; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 16px; margin: 0 10px; }
            .test-btn:hover { background: #f57c00; }
            .user-table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            .user-table th, .user-table td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
            .user-table th { background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; font-weight: bold; }
            .pro-user { background-color: #e8f5e8; }
            .free-user { background-color: #fff3e0; }
            .user-table tr:hover { background-color: #f0f0f0; }
            .no-users { text-align: center; padding: 40px; color: #666; font-style: italic; }
            .last-updated { text-align: center; margin-top: 20px; color: #666; font-size: 14px; }
            .auto-refresh-status { display: inline-block; margin-left: 10px; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
            .auto-refresh-on { background: #e8f5e8; color: #2e7d32; }
            .auto-refresh-off { background: #ffebee; color: #c62828; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>CSC 101 ADMIN MANAGEMENT BOARD</h1>
            </div>
            <!-- Display summary statistics -->
            <div class="stats">
                <h3>📊 User Statistics</h3>
                <div class="stat-grid">
                    <div class="stat-item">
                        <div class="stat-number">{{ total_users }}</div>
                        <div class="stat-label">Total Users</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{{ pro_users }}</div>
                        <div class="stat-label">Pro Users</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{{ free_users }}</div>
                        <div class="stat-label">Free Users</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{{ (pro_users / total_users * 100) | round(1) if total_users > 0 else 0 }}%</div>
                        <div class="stat-label">Pro Rate</div>
                    </div>
                </div>
            </div>
            
            <!-- Control buttons -->
            <div class="controls">
                <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Now</button>
                <button class="auto-refresh-btn" onclick="toggleAutoRefresh()">⏰ Auto Refresh</button>
                <button class="test-btn" onclick="testSignup()">🧪 Test Signup Process</button>
                <span id="autoRefreshStatus" class="auto-refresh-status auto-refresh-off">OFF</span>
            </div>
            
            <!-- Display user table -->
            <h3>👥 All Registered Users</h3>
            {% if users %}
            <table class="user-table">
                <thead>
                    <tr>
                        <th>🆔 User ID</th>
                        <th>📧 Email Address</th>
                        <th>💎 Account Type</th>
                        <th>🔐 Registration Method</th>
                    </tr>
                </thead>
                <tbody>
                    {% for user in users %}
                    <tr class="{{ 'pro-user' if user.is_pro else 'free-user' }}">
                        <td>{{ user.id }}</td>
                        <td>{{ user.email }}</td>
                        <td>{{ '💎 Pro User' if user.is_pro else '🆓 Free User' }}</td>
                        <td>{{ user.registration_method }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <div class="no-users">
                <h3>😔 No users found in database</h3>
                <p><strong>This means the OAuth2 callback is not working properly.</strong></p>
                <p>Users are signing up but not being saved to the database.</p>
                <p><a href="/" target="_blank">Try signing up again</a> and check server logs for errors.</p>
            </div>
            {% endif %}
            
            <div class="last-updated">
                📅 Last Updated: {{ generated_at }}
            </div>
        </div>

        <script>
            let autoRefreshInterval = null;
            let autoRefreshEnabled = false;

            function refreshData() {
                // Add timestamp to prevent caching
                const timestamp = new Date().getTime();
                window.location.href = window.location.pathname + '?t=' + timestamp;
            }

            function testSignup() {
                // Open signup page in new tab
                window.open('/', '_blank');
                alert('Please sign up with a new email in the opened tab, then come back here and click Refresh to see if it appears.');
            }

            function toggleAutoRefresh() {
                const button = document.querySelector('.auto-refresh-btn');
                const status = document.getElementById('autoRefreshStatus');
                
                if (autoRefreshEnabled) {
                    // Turn off auto refresh
                    clearInterval(autoRefreshInterval);
                    autoRefreshEnabled = false;
                    button.textContent = '⏰ Auto Refresh';
                    status.textContent = 'OFF';
                    status.className = 'auto-refresh-status auto-refresh-off';
                } else {
                    // Turn on auto refresh (every 10 seconds)
                    autoRefreshInterval = setInterval(refreshData, 10000);
                    autoRefreshEnabled = true;
                    button.textContent = '⏸️ Stop Auto Refresh';
                    status.textContent = 'ON (10s)';
                    status.className = 'auto-refresh-status auto-refresh-on';
                }
            }

            // Auto refresh data every 30 seconds if enabled
            function startAutoRefresh() {
                if (autoRefreshEnabled) {
                    setTimeout(refreshData, 30000);
                }
            }

            // Prevent caching
            window.addEventListener('pageshow', function(event) {
                if (event.persisted) {
                    window.location.reload();
                }
            });
        </script>
    </body>
    </html>
    """
      # Render the template with user data and add cache-busting headers
    response = make_response(render_template_string(html_template, **user_data))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@admin_bp.route('/users/api')

def get_users_api():
    """
    Admin API endpoint to get all OAuth2 users as JSON
    
    This endpoint returns raw JSON data for programmatic access
    Access: GET /admin/users/api
    
    Returns:
        JSON: Complete user data with statistics
    """
    # Get user data and return as JSON
    user_data = get_all_oauth_users()
    
    # Return JSON response with appropriate status code
    if user_data['success']:
        return jsonify(user_data), 200
    else:
        return jsonify(user_data), 500

@admin_bp.route('/users/count')
def get_user_count():
    """
    Quick endpoint to get just the user count statistics
    
    Access: GET /admin/users/count
    
    Returns:
        JSON: User count statistics only
    """
    try:
        # Get total user count from database
        total_users = User.query.count()
        
        # Count pro users
        pro_users = User.query.filter_by(is_pro=True).count()
        
        # Calculate free users
        free_users = total_users - pro_users
        
        return jsonify({
            'success': True,
            'total_users': total_users,
            'pro_users': pro_users,
            'free_users': free_users
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Additional utility function for searching users
def search_users_by_email(email_pattern):
    """
    Search for users by email pattern (for admin use)
    
    Args:
        email_pattern (str): Email pattern to search for
        
    Returns:
        list: List of matching users
    """
    try:
        # Use SQL LIKE pattern matching to find users
        matching_users = User.query.filter(
            User.email.like(f'%{email_pattern}%')
        ).all()
        
        # Convert to list of dictionaries
        user_list = []
        for user in matching_users:
            user_list.append({
                'id': user.id,
                'email': user.email,
                'is_pro': user.is_pro
            })
            
        return user_list
        
    except Exception as e:
        print(f"Error searching users: {e}")
        return []

