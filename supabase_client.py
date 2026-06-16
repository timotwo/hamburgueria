
from supabase import create_client

url = "https://ehejnrjaagavgvqygykh.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVoZWpucmphYWdhdmd2cXlneWtoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE1MzYxMjgsImV4cCI6MjA5NzExMjEyOH0.sDAB4Gx5xIkvdhL_kaRRBU-4oBjnYpCzAfn7I9UKxWA"

supabase = create_client(url, key)