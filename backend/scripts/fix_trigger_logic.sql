-- Исправление логики триггера update_verification_status
-- Проблема: Сначала проверяется срок, потом состояние
-- Правильно: Сначала проверить состояние, потом срок (только для state_work)

CREATE OR REPLACE FUNCTION public.update_verification_status()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
        DECLARE
            v_verification_due DATE;
            v_days_until_due INTEGER;
            v_new_status VARCHAR;
        BEGIN
            -- Calculate verification_due
            v_verification_due := (NEW.verification_date + make_interval(months => NEW.verification_interval) - interval '1 day')::date;
            v_days_until_due := v_verification_due - CURRENT_DATE;

            -- ИСПРАВЛЕННАЯ ЛОГИКА: Сначала проверяем состояние
            IF NEW.verification_state = 'state_storage' THEN
                v_new_status := 'status_storage';
            ELSIF NEW.verification_state = 'state_verification' THEN
                v_new_status := 'status_verification';
            ELSIF NEW.verification_state = 'state_repair' THEN
                v_new_status := 'status_repair';
            ELSIF NEW.verification_state = 'state_archived' THEN
                v_new_status := 'status_fit';
            ELSIF NEW.verification_state = 'state_work' THEN
                -- Только для состояния "В работе" проверяем срок
                IF CURRENT_DATE > v_verification_due THEN
                    v_new_status := 'status_expired';
                ELSIF v_days_until_due <= 14 THEN
                    v_new_status := 'status_expiring';
                ELSE
                    v_new_status := 'status_fit';
                END IF;
            ELSE
                v_new_status := 'status_fit';
            END IF;

            NEW.status := v_new_status;
            RETURN NEW;
        END;
        $function$
;
