import streamlit as st
import os
from db import LakebaseConnection

# Initialize database connection
db = LakebaseConnection()

# Get app-specific schema name
app_name = "help_desk_tickets"
client_id = os.environ["DATABRICKS_CLIENT_ID"]
schema = f"{app_name}_schema_{client_id}"

# Initialize database schema
def init_db():
    """Create tickets table if it doesn't exist"""
    db.execute_query(f"""
        CREATE SCHEMA IF NOT EXISTS {schema}
    """, fetch=False)
    
    db.execute_query(f"""
        CREATE TABLE IF NOT EXISTS {schema}.tickets (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            status VARCHAR(50) DEFAULT 'open',
            priority VARCHAR(20) DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """, fetch=False)

# Initialize on first run
init_db()

# Streamlit UI
st.title("Help Desk Tickets")

# Create new ticket
with st.form("new_ticket"):
    st.subheader("Create New Ticket")
    title = st.text_input("Title")
    description = st.text_area("Description")
    priority = st.selectbox("Priority", ["low", "medium", "high", "urgent"])
    
    if st.form_submit_button("Submit Ticket"):
        db.execute_query(
            f"""
            INSERT INTO {schema}.tickets (title, description, priority)
            VALUES (%s, %s, %s)
            """,
            (title, description, priority),
            fetch=False
        )
        st.success("Ticket created successfully!")
        st.rerun()

# Display tickets
st.subheader("Open Tickets")
tickets = db.execute_query(f"""
    SELECT id, title, description, status, priority, created_at
    FROM {schema}.tickets
    WHERE status != 'closed'
    ORDER BY created_at DESC
""")

for ticket in tickets:
    with st.expander(f"#{ticket[0]} - {ticket[1]} [{ticket[4]}]"):
        st.write(f"**Description:** {ticket[2]}")
        st.write(f"**Status:** {ticket[3]}")
        st.write(f"**Created:** {ticket[5]}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Mark as In Progress", key=f"progress_{ticket[0]}"):
                db.execute_query(
                    f"UPDATE {schema}.tickets SET status = 'in_progress' WHERE id = %s",
                    (ticket[0],),
                    fetch=False
                )
                st.rerun()
        
        with col2:
            if st.button(f"Close Ticket", key=f"close_{ticket[0]}"):
                db.execute_query(
                    f"UPDATE {schema}.tickets SET status = 'closed' WHERE id = %s",
                    (ticket[0],),
                    fetch=False
                )
                st.rerun()
