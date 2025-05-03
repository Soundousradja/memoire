function redirectToCategorySelection() {
    window.location.href = "{% url 'category_selection' %}";
    console.log(url);
    window.location.href = url; 
}