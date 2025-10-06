import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def connect_db():
    """Connect to PostgreSQL database"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'pagine_dev'),
        user=os.getenv('DB_USER', os.getenv('USER')),
        password=os.getenv('DB_PASSWORD', ''),
        port=os.getenv('DB_PORT', '5432')
    )

def find_duplicates(cursor):
    """Find duplicate movies based on (title, release_year, director)"""
    cursor.execute("""
        SELECT title, release_year, director, COUNT(*) as count
        FROM movie
        GROUP BY title, release_year, director
        HAVING COUNT(*) > 1
        ORDER BY count DESC, title
    """)
    return cursor.fetchall()

def remove_duplicates(cursor, conn):
    """Remove duplicate movies, keeping the one with the lowest id"""
    cursor.execute("""
        DELETE FROM movie
        WHERE id IN (
            SELECT id
            FROM (
                SELECT id,
                       ROW_NUMBER() OVER (
                           PARTITION BY title, release_year, director 
                           ORDER BY id
                       ) as row_num
                FROM movie
            ) t
            WHERE row_num > 1
        )
    """)
    deleted_count = cursor.rowcount
    conn.commit()
    return deleted_count

def main():
    conn = connect_db()
    cursor = conn.cursor()
    
    print("=" * 60)
    print("MOVIE DUPLICATE REMOVAL")
    print("=" * 60)
    
    # Find duplicates before removal
    print("\nSearching for duplicates...")
    duplicates = find_duplicates(cursor)
    
    if not duplicates:
        print("✓ No duplicates found! Database is clean.")
        cursor.close()
        conn.close()
        return
    
    print(f"\nFound {len(duplicates)} sets of duplicates:\n")
    
    total_duplicate_records = 0
    for title, year, director, count in duplicates:
        print(f"  • {title} ({year}) - {director}: {count} copies")
        total_duplicate_records += count
    
    print(f"\nTotal duplicate records: {total_duplicate_records}")
    print(f"Records to be removed: {total_duplicate_records - len(duplicates)}")
    
    # Confirm removal
    response = input("\nProceed with removal? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("Aborted. No changes made.")
        cursor.close()
        conn.close()
        return
    
    # Remove duplicates
    print("\nRemoving duplicates...")
    """
    cursor.execute("DELETE FROM watchlist")
    conn.commit()
    """
    deleted_count = remove_duplicates(cursor, conn)
    
    print(f"✓ Successfully removed {deleted_count} duplicate records")
    
    # Verify cleanup
    duplicates_after = find_duplicates(cursor)
    if not duplicates_after:
        print("✓ Database is now clean - no duplicates remain")
    else:
        print(f"⚠ Warning: {len(duplicates_after)} duplicate sets still exist")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    main()
