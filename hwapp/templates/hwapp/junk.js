                /* add new empty row to end of table */
                empty = document.getElementById(`new_hw_${row_id}`);
                table = document.getElementById('incomplete_table');



                /* update link and innerHTML */
                var new_class = document.getElementById(`new_hw_class_${row_id}`);
                new_class.innerHTML = result['class_name'] ;
                new_class.href = `/edit_hw/${result['hw_id']}`;
                

                var new_hw_title = document.getElementById(`new_hw_title_${row_id}`);
                new_hw_title.innerHTML = document.getElementById('hw_title').value;
                new_hw_title.href = `/edit_hw/${result['hw_id']}`;

                var new_due_date = document.getElementById(`new_due_date_${row_id}`);
                new_due_date.innerHTML = result['formatted_date'];
                new_due_date.href = `/edit_hw/${result['hw_id']}`;

                var new_priority = document.getElementById(`new_priority_${row_id}`);
                new_priority.innerHTML = document.getElementById('priority').value;
                new_priority.href = `/edit_hw/${result['hw_id']}`;
                
                /*increment id values*/
                values = empty.getElementsByTagName('a')
                values[0].id = `new_hw_title_${row_id+1}`
                values[1].id = `new_hw_class_${row_id+1}`
                values[2].id = `new_due_date_${row_id+1}`
                values[3].id = `new_priority_${row_id+1}`
                empty_new = `<tr class='index' id='new_hw_${row_id + 1}'>${empty.innerHTML}</tr>`;
                table.innerHTML += empty_new;

                /* create completioncall() onClick  for hw_id  */
                document.getElementById(`hwcheckbox_new_${row_id}`).onclick = `completioncall(${result['hw_id']})`;
                document.getElementById(`hwcheckbox_new_${row_id}`).value = false;

                /* show new checkbox */
                document.getElementById(`checkbox_${row_id}`).style.display = 'block';

                /* increment row ID, create new row with new row ID */
                row_id++;

                document.getElementById(`hwcheckbox_new_${row_id-1}`).id = `hwcheckbox_new_${row_id}`;
                document.getElementById(`checkbox_${row_id-1}`).id = `checkbox_${row_id}`;

                
                
                /* clear out fields */
                document.getElementById('hw_class').value = '';
                document.getElementById('hw_title').value = '';
                document.getElementById('due_date').value = '';
                document.getElementById('priority').value = '';

                /* autofocus on new row*/
                document.getElementById('hw_title').focus();