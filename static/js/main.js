  function update(data) {
          $('#loading').show()
          return fetch('/update', {
            method: 'put',
            body: JSON.stringify(data),
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            }
          })
            .then(checkStatus)
            .then(function() {
                $table.bootstrapTable('remove', {
                  field: 'productId',
                  values: data
              });
            })
            .then(() => $('#loading').show())
            .then(()=>console.log('updated!!!'))
        }

      function checkStatus(response) {
          if (response.status >= 200 && response.status < 300) {
            return response
          } else {
            var error = new Error(response.statusText)
            error.response = response
            throw error
          }
        }
          var $table = $('#table'),
              $button = $('#button');
              
    

      function api(){

        var data = [];
        fetch("/data")
        .then((resp) => resp.json())
        .then(function(res) {
            data = res
            console.log("API -data :"+res)
            $('#table').bootstrapTable('refreshOptions', {
                data: data
            });

        })
       
        return data
      }

      
      var test_data = api();
      console.log(JSON.stringify("parsed :"+test_data));
      $(function() {
       $('#table').bootstrapTable({
         data: test_data,
        
       });

     });
    


$(function () {
        $button.click(function () {
            var ids = $.map($table.bootstrapTable('getSelections'), function (row) {
                return row.productId;
            });
            console.log(ids);
            update(ids);
            
            $table.bootstrapTable('remove', {
                field: 'productId',
                values: ids
            });
        });
    });
   