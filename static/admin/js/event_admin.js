(function() {
    'use strict';
    
    function toggleTierFields() {
        const isFree = document.getElementById('id_is_free');
        if (!isFree) return;
        
        const tierFieldsets = document.querySelector('.field-tier_1_name')?.closest('fieldset');
        
        function updateVisibility() {
            if (tierFieldsets) {
                tierFieldsets.style.display = isFree.checked ? 'none' : 'block';
            }
        }
        
        isFree.addEventListener('change', updateVisibility);
        updateVisibility();
    }
    
    // Запуск після завантаження DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', toggleTierFields);
    } else {
        toggleTierFields();
    }
})();

