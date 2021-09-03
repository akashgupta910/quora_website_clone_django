
function AjaxLike(Question_url) {
    event.preventDefault();

    let action = "/question/like/";
    let method = "POST";

    $.ajax({
        url: action,
        type: method,
        data: {
            questionUrl: Question_url,
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
        },
        success: function (data) {
            console.log("success")
            console.log(data)
        },
        error: function (error) {
            console.log("error")
            console.log(error)
        }
    });
}

// def Like (request):     
//     if request.is_ajax():
//         url = request.POST.get("questionUrl")
//         user = Users.objects.get(email=request.session.get('email'))

//         likes = Question.objects.get(url=url).like
//         likes_array = likes.split(",")

//         for like in likes_array:
//             if like == user.username:
//                 likes_array.remove(like)
//             else:
//                 likes_array.append(user.username)

//         likes_str = ""
//         for i in likes_array:
//             likes_str += i + ","

//         return HttpResponse(likes_str)
//         Question.objects.filter(url=url).update(like=likes_str)

//         return HttpResponse(likes_str)

//         # like = Likes.objects.filter(user=user_obj, obj=question_obj)
        
//         # if like:
//         #     Likes.objects.get(user=user_obj, obj=question_obj).delete()
//         #     return HttpResponse("deleted")
        
//         # else:
//         #     Likes.objects.create(
//         #         user = user_obj,
//         #         obj = question_obj
//         #     )

//         #     return HttpResponse("Liked")     

//     else:
//         return redirect("home_page")