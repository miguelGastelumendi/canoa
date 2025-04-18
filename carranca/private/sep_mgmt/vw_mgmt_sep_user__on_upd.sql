-- DROP FUNCTION canoa.vw_mgmt_sep_user__on_upd();

CREATE OR REPLACE FUNCTION canoa.vw_mgmt_sep_user__on_upd()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
declare
	done_at timestamp;
	usr_new_name varchar(100);
    usr_curr_id int;
	usr_new_id int;
	-- fullname variable removed as it is unused
begin
    -- spell:ignore mgmt plpgsql
	-- adapted from `vw_mgmt_sep_user__on_upd` mgd 2024-10-25, 11-08
    -- mgd 2025-04-17

    -- TODO:
    -- Get message string from vw_ui_texts

	usr_new_name = Null;
	done_at = now();
	if NEW.sep_id is Null then
 		raise exception '[^|ID do SEP não foi informado.|^]';
    end if;
    -- save the current sep's ID
    select user_id into usr_curr_id from vw_mgmt_sep_user where sep_id = NEW.sep_id;

	if NEW.user_new is Null or trim(NEW.user_new) = '' then
		-- remove user's SEP
		usr_new_id := Null;
        if usr_curr_id is Null then
            return NEW; -- ignore, there in no current user
		end if;

	else -- find the user's ID from their name
		usr_new_name:= trim(NEW.user_new);
		select id into usr_new_id from canoa.users as usr where (usr.username_lower = lower(usr_new_name));

		if (usr_new_id is Null) then
 			raise exception '[^|Não foi encontrado o registro do usuário "%".|^]', usr_new_name;
		elsif usr_curr_id is Null then
            -- OK, no current user!
		elsif usr_curr_id = usr_new_id then
            return NEW; -- ignore, the new user is the same as the current user.
		end if;
	end if;


	-- Update canoa.sep table
	update canoa.sep
        set mgmt_users_id = usr_new_id
            ,mgmt_users_at = done_at
            ,mgmt_batch_code = NEW.batch_code -- traceability, see log_user_sep
        where id = NEW.sep_id;

	-- register operation on the log table
	insert into canoa.log_user_sep
		   		(id_users,    id_sep,     id_users_prior, done_at, done_by,         batch_code)
		 values (usr_new_id,  NEW.sep_id, usr_curr_id,    done_at, NEW.assigned_by, NEW.batch_code);

	return NEW;

end;
$function$
;

-- Permissions

ALTER FUNCTION canoa.vw_mgmt_sep_user__on_upd() OWNER TO canoa_power;
GRANT ALL ON FUNCTION canoa.vw_mgmt_sep_user__on_upd() TO canoa_power;
