document.addEventListener('DOMContentLoaded', function() {
    const addButton = document.querySelector('.add-btn');
    const ingredientBox = document.querySelector('.ingredient-box');

    // Add click event to the plus button
    addButton.addEventListener('click', function() {
        if (document.getElementById('input-container')) {
            return;
        }

        const inputContainer = document.createElement('div');
        inputContainer.id = 'input-container';

        const inputField = document.createElement('input');
        inputField.type = 'text';
        inputField.id = 'nouvel-ingredient';
        inputField.placeholder = 'Nouvel ingrédient';
        inputField.classList.add('nouvel-ingredient-input');

        const ajouterBtn = document.createElement('button');
        ajouterBtn.textContent = 'Ajouter';
        ajouterBtn.id = 'btn-ajouter';
        ajouterBtn.classList.add('ajouter-btn');

        inputContainer.appendChild(inputField);
        inputContainer.appendChild(ajouterBtn);

        ingredientBox.insertBefore(inputContainer, addButton);

        inputField.focus();

        ajouterBtn.addEventListener('click', addNewIngredient);

        inputField.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                addNewIngredient();
            }
        });
    });

    function addNewIngredient() {
        const inputField = document.getElementById('nouvel-ingredient');
        const ingredientName = inputField.value.trim().toUpperCase();

        if (!ingredientName) {
            alert('Veuillez entrer un nom d\'ingrédient');
            return;
        }

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const formData = new FormData();
        formData.append('name', ingredientName);

        const url = "/super/ingredient_management/";
        fetch(url, {
            method: "POST",
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Ingrédient ajouté') {
                const newIngredientButton = document.createElement('button');
                newIngredientButton.classList.add('ingredient');
                newIngredientButton.textContent = data.ingredient;
                ingredientBox.insertBefore(newIngredientButton, addButton);
            } else {
                alert('Erreur lors de l\'ajout de l\'ingrédient');
            }
        })
        .catch(error => console.error('Erreur :', error));
    }

    
    });

