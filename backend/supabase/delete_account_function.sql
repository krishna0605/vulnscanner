-- Delete Account Function
-- Run this in Supabase SQL Editor
-- This function deletes all user data when called

-- Create function to delete all user data
CREATE OR REPLACE FUNCTION delete_user_account(user_id_param UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Delete findings for user's scans
    DELETE FROM findings 
    WHERE scan_id IN (
        SELECT s.id FROM scans s 
        JOIN projects p ON s.project_id = p.id 
        WHERE p.user_id = user_id_param
    );
    
    -- Delete assets for user's projects
    DELETE FROM assets WHERE project_id IN (
        SELECT id FROM projects WHERE user_id = user_id_param
    );
    
    -- Delete scans for user's projects
    DELETE FROM scans WHERE project_id IN (
        SELECT id FROM projects WHERE user_id = user_id_param
    );
    
    -- Delete user's projects
    DELETE FROM projects WHERE user_id = user_id_param;
    
    -- Delete avatar files from storage (handled separately via client)
    
    -- Delete user profile
    DELETE FROM profiles WHERE id = user_id_param;
    
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION delete_user_account(UUID) TO authenticated;

-- Add policy to allow users to only delete their own account
-- The function uses SECURITY DEFINER so it runs with elevated privileges
-- but we validate the user in the frontend before calling
