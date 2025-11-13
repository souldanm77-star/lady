// web/js/main.js

// =================================================================
// VARIABLES GLOBALES ET ÉTAT DE L'APPLICATION
// =================================================================

let cart = [];
let currentPage = 1;
const itemsPerPage = 9; // Nombre de produits par page
let filteredProducts = [];
const allProducts = []; // Garde une copie non filtrée de tous les produits

// =================================================================
// FONCTIONS D'INITIALISATION AU CHARGEMENT DE LA PAGE
// =================================================================

document.addEventListener('DOMContentLoaded', function () {
    // Vérifie si les produits sont chargés depuis products.js
    if (typeof products !== 'undefined' && products.length > 0) {
        allProducts.length = 0; // Vide le tableau
        allProducts.push(...products); // Copie tous les produits
        filteredProducts.length = 0;
        filteredProducts.push(...allProducts); // Initialise les produits filtrés

        displayFeaturedProducts();
        displayProducts();
        updateCartCount();
    } else {
        console.warn("Aucun produit trouvé dans la variable 'products'.");
        // Affiche un message si aucun produit n'est trouvé
        const productsGrid = document.getElementById('productsGrid');
        if (productsGrid) {
            productsGrid.innerHTML = '<p style="grid-column: 1 / -1; text-align: center; padding: 2rem;">Aucun produit trouvé. Veuillez exporter les produits depuis l\'application de gestion.</p>';
        }
    }
});

// =================================================================
// FONCTIONS UTILITAIRES
// =================================================================

function formatPrice(price) {
    const p = parseFloat(price);
    return `${p.toFixed(2).replace('.', ',')}€`;
}

function getImagePath(product) {
    // CORRECTION : Le chemin de l'image doit être relatif au fichier HTML (qui est dans /web/)
    // Python sauvegarde dans 'images/produits/...' donc depuis le HTML, il faut remonter d'un niveau.
    if (product.image_path) {
        return `../${product.image_path}`;
    }
    return null; // Pas d'image, on utilisera l'icône
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    const colors = {
        'success': '#10b981',
        'error': '#ef4444',
        'warning': '#f59e0b',
        'info': '#2563eb'
    };
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: ${colors[type] || colors.info};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 3000;
        opacity: 0;
        transition: opacity 0.3s ease-in-out;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => { toast.style.opacity = '1'; }, 100);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => { if (document.body.contains(toast)) document.body.removeChild(toast); }, 300);
    }, 3000);
}

// =================================================================
// FONCTIONS D'AFFICHAGE DES PRODUITS
// =================================================================

function displayProducts() {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;

    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageProducts = filteredProducts.slice(startIndex, endIndex);

    grid.innerHTML = pageProducts.map(product => {
        const imageSrc = getImagePath(product);
        const imageHtml = imageSrc ? `<img src="${imageSrc}" alt="${product.name}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                                        <div style="display:none; align-items:center; justify-content:center; height:100%; font-size: 3rem;">${product.icon || '📦'}</div>`
            : `<div style="display:flex; align-items:center; justify-content:center; height:100%; font-size: 3rem;">${product.icon || '📦'}</div>`;

        return `
        <div class="product-card" onclick="openProductDetail(${product.id})">
            <div class="product-image">
                ${imageHtml}
                ${product.badge ? `<span class="product-badge">${product.badge}</span>` : ''}
            </div>
            <div class="product-info">
                <p class="product-category">${product.category || 'Non catégorisé'}</p>
                <h3>${product.name}</h3>
                <div class="product-rating">${'⭐'.repeat(product.rating || 5)}</div>
                <p class="product-price">${formatPrice(product.price)}</p>
                <button class="btn-add-cart" onclick="event.stopPropagation(); addToCart(${product.id})">
                    Ajouter au panier
                </button>
            </div>
        </div>
    `;
    }).join('');

    updatePagination();
}

function displayFeaturedProducts() {
    const grid = document.getElementById('featuredProducts');
    if (!grid) return;

    // On considère un produit comme "phare" s'il a un badge
    // On utilise 'allProducts' pour toujours avoir la liste complète
    const featured = allProducts.filter(p => p.badge).slice(0, 3);

    grid.innerHTML = featured.map(product => {
        const imageSrc = getImagePath(product);
        const imageHtml = imageSrc ? `<img src="${imageSrc}" alt="${product.name}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                                        <div style="display:none; align-items:center; justify-content:center; height:100%; font-size: 3rem;">${product.icon || '📦'}</div>`
            : `<div style="display:flex; align-items:center; justify-content:center; height:100%; font-size: 3rem;">${product.icon || '📦'}</div>`;

        return `
        <div class="product-card" onclick="openProductDetail(${product.id})">
            <div class="product-image">
                ${imageHtml}
                <span class="product-badge">${product.badge}</span>
            </div>
            <div class="product-info">
                <p class="product-category">${product.category || 'Non catégorisé'}</p>
                <h3>${product.name}</h3>
                <div class="product-rating">${'⭐'.repeat(product.rating || 5)}</div>
                <p class="product-price">${formatPrice(product.price)}</p>
                <button class="btn-add-cart" onclick="event.stopPropagation(); addToCart(${product.id})">
                    Ajouter au panier
                </button>
            </div>
        </div>
    `;
    }).join('');
}

// =================================================================
// FONCTIONS DE FILTRAGE ET DE TRI
// =================================================================

function searchProducts() {
    const query = document.getElementById('searchBox').value.toLowerCase();
    filteredProducts = allProducts.filter(p =>
        p.name.toLowerCase().includes(query) ||
        p.category.toLowerCase().includes(query)
    );
    currentPage = 1;
    displayProducts();
}

function filterProducts() {
    const category = document.getElementById('categoryFilter').value;
    if (category) {
        filteredProducts = allProducts.filter(p => p.category === category);
    } else {
        filteredProducts = [...allProducts];
    }
    currentPage = 1;
    displayProducts();
}

function sortProducts() {
    const sortType = document.getElementById('sortFilter').value;

    switch (sortType) {
        case 'price-asc':
            filteredProducts.sort((a, b) => a.price - b.price);
            break;
        case 'price-desc':
            filteredProducts.sort((a, b) => b.price - a.price);
            break;
        case 'name':
            filteredProducts.sort((a, b) => a.name.localeCompare(b.name));
            break;
        default:
            filteredProducts.sort((a, b) => a.id - b.id);
            break;
    }
    displayProducts();
}

function filterByCategory(category) {
    showPage('products');
    document.getElementById('categoryFilter').value = category;
    filterProducts();
}

// =================================================================
// FONCTIONS DE PAGINATION
// =================================================================

function updatePagination() {
    const paginationContainer = document.getElementById('pagination');
    if (!paginationContainer) return;

    const totalPages = Math.ceil(filteredProducts.length / itemsPerPage);
    let html = '';

    for (let i = 1; i <= totalPages; i++) {
        html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="changePage(${i})">${i}</button>`;
    }
    paginationContainer.innerHTML = html;
}

function changePage(page) {
    currentPage = page;
    displayProducts();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// =================================================================
// FONCTIONS DU PANIER
// =================================================================

function addToCart(productId) {
    const product = allProducts.find(p => p.id === productId);
    if (!product) return;

    const existingItem = cart.find(item => item.id === productId);

    if (existingItem) {
        existingItem.quantity++;
    } else {
        cart.push({ ...product, quantity: 1 });
    }

    updateCartCount();
    showToast(`✓ ${product.name} ajouté au panier !`, 'success');
}

function updateCartCount() {
    const count = cart.reduce((sum, item) => sum + item.quantity, 0);
    const countElement = document.getElementById('cartCount');
    if (countElement) {
        countElement.textContent = count;
    }
}

function displayCart() {
    const cartItemsContainer = document.getElementById('cartItems');
    if (!cartItemsContainer) return;

    if (cart.length === 0) {
        cartItemsContainer.innerHTML = '<p style="text-align: center; padding: 3rem;">Votre panier est vide</p>';
        updateCartSummary();
        return;
    }

    cartItemsContainer.innerHTML = cart.map(item => {
        const imageSrc = getImagePath(item);
        const imageHtml = imageSrc ? `<img src="${imageSrc}" alt="${item.name}" style="width:100%; height:100%; object-fit:cover;">` : item.icon || '📦';

        return `
        <div class="cart-item">
            <div class="cart-item-image">
                ${imageHtml}
            </div>
            <div class="cart-item-details">
                <h3>${item.name}</h3>
                <p class="product-category">${item.category}</p>
                <p class="product-price">${formatPrice(item.price)}</p>
                <div class="quantity-controls">
                    <button class="quantity-btn" onclick="updateQuantity(${item.id}, -1)">-</button>
                    <span style="font-weight: bold;">${item.quantity}</span>
                    <button class="quantity-btn" onclick="updateQuantity(${item.id}, 1)">+</button>
                    <span class="remove-btn" onclick="removeFromCart(${item.id})">🗑️ Supprimer</span>
                </div>
            </div>
            <div style="font-weight: bold; font-size: 1.2rem;">
                ${formatPrice(item.price * item.quantity)}
            </div>
        </div>
    `;
    }).join('');

    updateCartSummary();
}

function updateQuantity(productId, change) {
    const item = cart.find(i => i.id === productId);
    if (item) {
        item.quantity += change;
        if (item.quantity <= 0) {
            removeFromCart(productId);
        } else {
            displayCart();
            updateCartCount();
        }
    }
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    displayCart();
    updateCartCount();
}

function updateCartSummary() {
    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const shipping = subtotal >= 50 ? 0 : 5.00;
    const total = subtotal + shipping;

    const subtotalElement = document.getElementById('subtotal');
    const shippingElement = document.getElementById('shipping');
    const totalElement = document.getElementById('total');
    const checkoutTotalElement = document.getElementById('checkoutTotal');

    if (subtotalElement) subtotalElement.textContent = formatPrice(subtotal);
    if (shippingElement) shippingElement.textContent = shipping === 0 ? 'GRATUIT' : formatPrice(shipping);
    if (totalElement) totalElement.textContent = formatPrice(total);
    if (checkoutTotalElement) checkoutTotalElement.textContent = formatPrice(total);
}

// =================================================================
// FONCTIONS DE LA MODALE DE DÉTAIL PRODUIT
// =================================================================

function openProductDetail(productId) {
    const product = allProducts.find(p => p.id === productId);
    if (!product) return;

    const modal = document.getElementById('productModal');
    const detailContainer = document.getElementById('productDetail');
    if (!modal || !detailContainer) return;

    const imageSrc = getImagePath(product);
    const imageHtml = imageSrc ? `<img src="${imageSrc}" alt="${product.name}" style="width:100%; height:100%; object-fit:cover;">` : product.icon || '📦';

    detailContainer.innerHTML = `
        <div class="product-detail-image">
            ${imageHtml}
        </div>
        <div>
            <p class="product-category">${product.category}</p>
            <h2 style="margin-bottom: 1rem;">${product.name}</h2>
            <div class="product-rating" style="margin-bottom: 1rem;">${'⭐'.repeat(product.rating || 5)}</div>
            <p class="product-price" style="margin-bottom: 2rem;">${formatPrice(product.price)}</p>
            
            <h3 style="margin-bottom: 1rem;">Description</h3>
            <p style="line-height: 1.8; margin-bottom: 2rem;">
                ${product.description || 'Aucune description disponible pour ce produit.'}
            </p>
            
            <button class="btn-add-cart" onclick="addToCart(${product.id}); closeModal();" style="width: 100%; padding: 1rem;">
                Ajouter au panier - ${formatPrice(product.price)}
            </button>
        </div>
    `;

    modal.classList.add('active');
}

function closeModal() {
    const modal = document.getElementById('productModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Fermer la modal en cliquant en dehors
window.onclick = function (event) {
    const modal = document.getElementById('productModal');
    if (event.target === modal) {
        closeModal();
    }
}

// =================================================================
// FONCTIONS DE NAVIGATION ENTRE LES PAGES
// =================================================================

function showPage(pageName) {
    document.querySelectorAll('.page-content').forEach(page => {
        page.classList.remove('active');
    });

    const targetPage = document.getElementById(pageName + 'Page');
    if (targetPage) {
        targetPage.classList.add('active');
    }

    const navLinks = document.getElementById('navLinks');
    if (navLinks) {
        navLinks.classList.remove('active');
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });

    if (pageName === 'cart') {
        displayCart();
    } else if (pageName === 'checkout') {
        updateCartSummary();
    }
}

function toggleMenu() {
    const navLinks = document.getElementById('navLinks');
    if (navLinks) {
        navLinks.classList.toggle('active');
    }
}

// =================================================================
// GESTION DU CAROUSEL (plus sûr)
// =================================================================

function goToSlide(index) {
    const carousel = document.getElementById('carousel');
    const dots = document.querySelectorAll('.carousel-dot');
    if (!carousel) return;

    currentSlide = index;
    carousel.style.transform = `translateX(-${currentSlide * 100}%)`;

    dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === currentSlide);
    });
}

// Auto-rotation du carousel uniquement si on est sur la page d'accueil
setInterval(() => {
    const homePage = document.getElementById('homePage');
    if (homePage && homePage.classList.contains('active')) {
        const slides = document.querySelectorAll('.carousel-slide');
        if (slides.length > 0) {
            currentSlide = (currentSlide + 1) % slides.length;
            goToSlide(currentSlide);
        }
    }
}, 5000);

// =================================================================
// GESTION DES FORMULAIRES
// =================================================================

function submitOrder(event) {
    event.preventDefault();
    alert('✓ Commande confirmée ! Merci pour votre achat. Vous recevrez un email de confirmation sous peu.');
    cart = [];
    updateCartCount();
    showPage('home');
}

function submitContact(event) {
    event.preventDefault();
    alert('✓ Message envoyé ! Notre équipe vous répondra dans les plus brefs délais.');
    event.target.reset();
}