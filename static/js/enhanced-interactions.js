/**
 * Enhanced Interactions - Modern, fluid, intuitive and interactive behaviors
 */
document.addEventListener('DOMContentLoaded', function() {
  // Initialize animations with delay for smoother page load
  setTimeout(() => {
    document.body.classList.add('animations-enabled');
  }, 300);
  
  // Mobile menu toggle functionality
  const menuToggle = document.querySelector('.menu-toggle');
  const navLinks = document.querySelector('.nav-links');
  
  if (menuToggle && navLinks) {
    menuToggle.addEventListener('click', function() {
      navLinks.classList.toggle('show');
      // Add animation
      if (navLinks.classList.contains('show')) {
        animateNavItems();
      }
    });
  }
  
  // Animate nav items sequentially
  function animateNavItems() {
    const navItems = document.querySelectorAll('.nav-links .nav-link');
    navItems.forEach((item, index) => {
      item.style.animationDelay = `${index * 0.1}s`;
      item.classList.add('nav-item-animate');
    });
  }
  
  // Set active nav link based on current page with highlight effect
  const currentPage = window.location.pathname;
  const navLinksItems = document.querySelectorAll('.nav-link');
  
  navLinksItems.forEach(link => {
    if (link.getAttribute('href') && currentPage.includes(link.getAttribute('href'))) {
      link.classList.add('active');
      link.insertAdjacentHTML('beforeend', '<span class="active-indicator"></span>');
    }
    
    // Add hover effects
    link.addEventListener('mouseenter', function() {
      if (!this.classList.contains('active')) {
        this.classList.add('hover-effect');
      }
    });
    
    link.addEventListener('mouseleave', function() {
      this.classList.remove('hover-effect');
    });
  });
  
  // Enhanced scroll behavior
  const scrollElements = document.querySelectorAll('[data-scroll-to]');
  scrollElements.forEach(element => {
    element.addEventListener('click', function(e) {
      e.preventDefault();
      const targetId = this.getAttribute('data-scroll-to');
      const targetElement = document.querySelector(targetId);
      
      if (targetElement) {
        // Highlight target temporarily
        targetElement.classList.add('scroll-highlight');
        
        // Smooth scroll with offset
        const headerHeight = document.querySelector('.app-header')?.offsetHeight || 0;
        const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - headerHeight - 20;
        
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
        
        // Remove highlight after animation
        setTimeout(() => {
          targetElement.classList.remove('scroll-highlight');
        }, 2000);
      }
    });
  });
  
  // Message reactions functionality
  function initializeMessageReactions() {
    const messages = document.querySelectorAll('.message');
    
    messages.forEach(message => {
      // Add reaction button to message actions
      const messageContent = message.querySelector('.message-content');
      if (messageContent && !message.querySelector('.message-actions')) {
        const actionsContainer = document.createElement('div');
        actionsContainer.className = 'message-actions';
        actionsContainer.innerHTML = `
          <button class="message-action-btn reaction-btn" title="Ajouter une réaction">
            <i class="far fa-smile"></i>
          </button>
          <button class="message-action-btn reply-btn" title="Répondre">
            <i class="fas fa-reply"></i>
          </button>
          <button class="message-action-btn copy-btn" title="Copier le message">
            <i class="far fa-copy"></i>
          </button>
          <button class="message-action-btn more-btn" title="Plus d'options">
            <i class="fas fa-ellipsis-h"></i>
          </button>
        `;
        
        messageContent.parentNode.appendChild(actionsContainer);
        
        // Create reaction container if not exists
        if (!message.querySelector('.reaction-container')) {
          const reactionContainer = document.createElement('div');
          reactionContainer.className = 'reaction-container';
          messageContent.parentNode.appendChild(reactionContainer);
        }
      }
    });
    
    // Handle reaction button clicks
    document.querySelectorAll('.reaction-btn').forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        showReactionPicker(this);
      });
    });
    
    // Handle reply button clicks
    document.querySelectorAll('.reply-btn').forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        const message = this.closest('.message');
        showReplyInterface(message);
      });
    });
    
    // Handle copy button clicks
    document.querySelectorAll('.copy-btn').forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        const message = this.closest('.message');
        const messageText = message.querySelector('.message-content').textContent.trim();
        copyToClipboard(messageText);
        showFeedbackToast('Message copié dans le presse-papier');
      });
    });
  }
  
  // Show reaction picker
  function showReactionPicker(button) {
    const message = button.closest('.message');
    const existingPicker = document.querySelector('.reaction-picker');
    
    if (existingPicker) {
      existingPicker.remove();
      return;
    }
    
    const reactionPicker = document.createElement('div');
    reactionPicker.className = 'reaction-picker';
    reactionPicker.innerHTML = `
      <div class="reaction-picker-content">
        <span class="emoji-option" data-emoji="👍">👍</span>
        <span class="emoji-option" data-emoji="❤️">❤️</span>
        <span class="emoji-option" data-emoji="😂">😂</span>
        <span class="emoji-option" data-emoji="😮">😮</span>
        <span class="emoji-option" data-emoji="😢">😢</span>
        <span class="emoji-option" data-emoji="👏">👏</span>
        <span class="emoji-option" data-emoji="🙏">🙏</span>
      </div>
    `;
    
    button.parentNode.appendChild(reactionPicker);
    
    // Animate picker appearance
    setTimeout(() => {
      reactionPicker.classList.add('reaction-picker-visible');
    }, 10);
    
    // Handle emoji selection
    reactionPicker.querySelectorAll('.emoji-option').forEach(emoji => {
      emoji.addEventListener('click', function() {
        const emojiValue = this.getAttribute('data-emoji');
        addReaction(message, emojiValue);
        reactionPicker.remove();
      });
    });
    
    // Close picker when clicking elsewhere
    document.addEventListener('click', function closeReactionPicker(e) {
      if (!reactionPicker.contains(e.target) && e.target !== button) {
        reactionPicker.remove();
        document.removeEventListener('click', closeReactionPicker);
      }
    });
  }
  
  // Add a reaction to a message
  function addReaction(message, emoji) {
    const reactionContainer = message.querySelector('.reaction-container');
    const existingReaction = reactionContainer.querySelector(`[data-emoji="${emoji}"]`);
    
    if (existingReaction) {
      // Increment counter if reaction already exists
      const countEl = existingReaction.querySelector('.count');
      const count = parseInt(countEl.textContent, 10) + 1;
      countEl.textContent = count;
      
      // Animate the increment
      existingReaction.classList.add('reaction-pulsate');
      setTimeout(() => {
        existingReaction.classList.remove('reaction-pulsate');
      }, 500);
    } else {
      // Create new reaction
      const reactionEl = document.createElement('div');
      reactionEl.className = 'reaction-bubble';
      reactionEl.setAttribute('data-emoji', emoji);
      reactionEl.innerHTML = `
        <span class="emoji">${emoji}</span>
        <span class="count">1</span>
      `;
      
      reactionContainer.appendChild(reactionEl);
      
      // Animate new reaction
      reactionEl.classList.add('reaction-appear');
      setTimeout(() => {
        reactionEl.classList.remove('reaction-appear');
      }, 500);
    }
  }
  
  // Show reply interface
  function showReplyInterface(message) {
    const messageContainer = document.querySelector('.messages-container');
    const inputContainer = document.querySelector('.input-container');
    const messageContent = message.querySelector('.message-content').textContent.trim();
    const senderName = message.querySelector('.message-avatar').textContent.trim();
    
    // Remove existing reply interface if any
    const existingReplyInterface = document.querySelector('.reply-interface');
    if (existingReplyInterface) {
      existingReplyInterface.remove();
    }
    
    // Create reply interface
    const replyInterface = document.createElement('div');
    replyInterface.className = 'reply-interface';
    replyInterface.innerHTML = `
      <div class="reply-header">
        <i class="fas fa-reply"></i>
        <span>Répondre à <strong>${senderName}</strong></span>
        <button class="close-reply-btn"><i class="fas fa-times"></i></button>
      </div>
      <div class="reply-preview">${messageContent.length > 50 ? messageContent.substring(0, 50) + '...' : messageContent}</div>
    `;
    
    // Insert before input container
    inputContainer.insertBefore(replyInterface, inputContainer.firstChild);
    
    // Animate appearance
    setTimeout(() => {
      replyInterface.classList.add('reply-interface-visible');
    }, 10);
    
    // Focus input field
    const inputField = document.querySelector('.message-input');
    if (inputField) {
      inputField.focus();
    }
    
    // Close reply interface
    replyInterface.querySelector('.close-reply-btn').addEventListener('click', function() {
      replyInterface.classList.remove('reply-interface-visible');
      setTimeout(() => {
        replyInterface.remove();
      }, 300);
    });
  }
  
  // Copy text to clipboard
  function copyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
      document.execCommand('copy');
    } catch (err) {
      console.error('Could not copy text: ', err);
    }
    
    document.body.removeChild(textArea);
  }
  
  // Show feedback toast
  function showFeedbackToast(message) {
    const existingToast = document.querySelector('.feedback-toast');
    if (existingToast) {
      existingToast.remove();
    }
    
    const toast = document.createElement('div');
    toast.className = 'feedback-toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    // Animate toast
    setTimeout(() => {
      toast.classList.add('feedback-toast-visible');
      
      // Auto-hide after delay
      setTimeout(() => {
        toast.classList.remove('feedback-toast-visible');
        setTimeout(() => {
          toast.remove();
        }, 300);
      }, 3000);
    }, 10);
  }
  
  // Enhanced typing indicator
  const inputField = document.querySelector('.message-input');
  if (inputField) {
    let typingTimer;
    
    inputField.addEventListener('input', function() {
      // Show typing indicator to recipient
      // In real app, this would trigger a websocket event
      clearTimeout(typingTimer);
      
      // Stop typing indicator after delay
      typingTimer = setTimeout(() => {
        // In real app, this would trigger a websocket event to stop typing indicator
      }, 3000);
    });
  }
  
  // Enhanced message send with animations
  const sendButton = document.querySelector('.send-button');
  if (sendButton && inputField) {
    sendButton.addEventListener('click', function() {
      if (inputField.value.trim() !== '') {
        sendMessageWithAnimation(inputField.value.trim());
        inputField.value = '';
      } else {
        // Shake animation for empty messages
        sendButton.classList.add('shake-animation');
        setTimeout(() => {
          sendButton.classList.remove('shake-animation');
        }, 500);
      }
    });
    
    // Send on Enter key
    inputField.addEventListener('keypress', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendButton.click();
      }
    });
  }
  
  // Send message with animation
  function sendMessageWithAnimation(messageText) {
    const messagesContainer = document.querySelector('.messages-container');
    if (!messagesContainer) return;
    
    // Check for reply context
    const replyInterface = document.querySelector('.reply-interface');
    let replyContext = null;
    
    if (replyInterface) {
      replyContext = {
        text: replyInterface.querySelector('.reply-preview').textContent,
        author: replyInterface.querySelector('strong').textContent
      };
      
      // Remove reply interface
      replyInterface.classList.remove('reply-interface-visible');
      setTimeout(() => {
        replyInterface.remove();
      }, 300);
    }
    
    // Create message element
    const message = document.createElement('div');
    message.className = 'message outgoing message-sending';
    
    let messageHTML = `
      <div class="message-content-wrapper">
        <div class="message-avatar">T</div>
        <div class="message-content">
    `;
    
    // Add reply reference if applicable
    if (replyContext) {
      messageHTML += `
        <div class="message-reply-ref">
          <div class="reply-author">${replyContext.author}</div>
          <div class="reply-text">${replyContext.text}</div>
        </div>
      `;
    }
    
    // Add message text
    messageHTML += `${messageText}</div>
      </div>
      <span class="message-time">${getCurrentTime()}</span>
      <div class="message-status status-sending">
        <i class="fas fa-circle-notch fa-spin status-icon"></i>
        <span>Envoi en cours...</span>
      </div>
    `;
    
    message.innerHTML = messageHTML;
    
    // Append to container
    messagesContainer.appendChild(message);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Simulate sending delay
    setTimeout(() => {
      message.classList.remove('message-sending');
      message.classList.add('message-sent');
      
      // Update status
      const statusEl = message.querySelector('.message-status');
      statusEl.className = 'message-status status-sent';
      statusEl.innerHTML = `
        <i class="fas fa-check status-icon"></i>
        <span>Envoyé</span>
      `;
      
      // Simulate delivery status update
      setTimeout(() => {
        statusEl.className = 'message-status status-delivered';
        statusEl.innerHTML = `
          <i class="fas fa-check-double status-icon"></i>
          <span>Remis</span>
        `;
        
        // Simulate read status update
        setTimeout(() => {
          statusEl.className = 'message-status status-read';
          statusEl.innerHTML = `
            <i class="fas fa-check-double status-icon"></i>
            <span>Lu</span>
          `;
          
          // Add reactions capability
          initializeMessageReactions();
          
          // Simulate reply after 2-4 seconds
          simulateReply();
        }, 2000);
      }, 1500);
    }, 1000);
  }
  
  // Get current time formatted
  function getCurrentTime() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
  }
  
  // Simulate reply from the other person
  function simulateReply() {
    const messagesContainer = document.querySelector('.messages-container');
    if (!messagesContainer) return;
    
    // Simulate typing indicator
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.innerHTML = `
      <span class="typing-avatar">J</span>
      <div class="typing-bubble"></div>
      <div class="typing-bubble"></div>
      <div class="typing-bubble"></div>
    `;
    
    messagesContainer.appendChild(typingIndicator);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Simulate reply after typing delay
    const replyDelay = Math.random() * 2000 + 2000; // 2-4 seconds
    
    setTimeout(() => {
      // Remove typing indicator
      typingIndicator.remove();
      
      // Create reply message
      const replyMessages = [
        "Merci pour votre message, je vais examiner cela.",
        "C'est noté, je reviens vers vous rapidement.",
        "Parfait, merci pour ces informations !",
        "Je comprends, pouvons-nous en discuter plus en détail lors d'un appel ?",
        "Bien reçu, je vais préparer les documents nécessaires."
      ];
      
      const randomIndex = Math.floor(Math.random() * replyMessages.length);
      const replyText = replyMessages[randomIndex];
      
      const reply = document.createElement('div');
      reply.className = 'message incoming message-appearing';
      reply.innerHTML = `
        <div class="message-content-wrapper">
          <div class="message-avatar">J</div>
          <div class="message-content">${replyText}</div>
        </div>
        <span class="message-time">${getCurrentTime()}</span>
      `;
      
      messagesContainer.appendChild(reply);
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
      
      // Animation for appearing
      setTimeout(() => {
        reply.classList.remove('message-appearing');
        
        // Add reactions capability
        initializeMessageReactions();
      }, 100);
    }, replyDelay);
  }
  
  // Initialize message reactions for existing messages
  initializeMessageReactions();
  
  // Add mobile swipe actions
  if (window.innerWidth <= 768) {
    initializeMobileSwipeActions();
  }
  
  function initializeMobileSwipeActions() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
      let touchStartX = 0;
      let touchEndX = 0;
      
      // Add swipe actions container if not exists
      if (!message.querySelector('.message-swipe-actions')) {
        const swipeActionsContainer = document.createElement('div');
        swipeActionsContainer.className = 'message-swipe-actions';
        swipeActionsContainer.innerHTML = `
          <div class="message-swipe-action swipe-action-reply" data-action="reply">
            <i class="fas fa-reply"></i>
          </div>
          <div class="message-swipe-action swipe-action-forward" data-action="forward">
            <i class="fas fa-share"></i>
          </div>
          <div class="message-swipe-action swipe-action-delete" data-action="delete">
            <i class="fas fa-trash-alt"></i>
          </div>
        `;
        
        message.appendChild(swipeActionsContainer);
      }
      
      // Touch events for swipe
      message.addEventListener('touchstart', function(e) {
        touchStartX = e.touches[0].clientX;
      });
      
      message.addEventListener('touchmove', function(e) {
        touchEndX = e.touches[0].clientX;
        const diffX = touchStartX - touchEndX;
        
        // If swiping left (positive diff)
        if (diffX > 50 && diffX < 150) {
          this.style.transform = `translateX(-${diffX}px)`;
        }
      });
      
      message.addEventListener('touchend', function() {
        const diffX = touchStartX - touchEndX;
        
        if (diffX > 100) {
          // Complete the swipe
          this.classList.add('swiped-left');
        } else {
          // Reset position
          this.style.transform = '';
        }
      });
      
      // Handle swipe action clicks
      const swipeActions = message.querySelectorAll('.message-swipe-action');
      swipeActions.forEach(action => {
        action.addEventListener('click', function() {
          const actionType = this.getAttribute('data-action');
          handleSwipeAction(message, actionType);
          
          // Reset swipe
          setTimeout(() => {
            message.classList.remove('swiped-left');
            message.style.transform = '';
          }, 300);
        });
      });
    });
  }
  
  // Handle swipe actions
  function handleSwipeAction(message, actionType) {
    switch (actionType) {
      case 'reply':
        showReplyInterface(message);
        break;
      case 'forward':
        showFeedbackToast('Transfer de message...');
        break;
      case 'delete':
        message.classList.add('message-deleting');
        setTimeout(() => {
          message.remove();
        }, 300);
        break;
    }
  }
  
  // Add scroll reveal animations
  const scrollRevealElements = document.querySelectorAll('.scroll-reveal');
  
  if (scrollRevealElements.length > 0) {
    const observerOptions = {
      root: null,
      rootMargin: '0px',
      threshold: 0.1
    };
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('reveal-visible');
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);
    
    scrollRevealElements.forEach(element => {
      observer.observe(element);
    });
  }
  
  // Add a subtle parallax effect
  if (window.innerWidth > 768) {
    window.addEventListener('mousemove', function(e) {
      const mouseX = e.clientX / window.innerWidth;
      const mouseY = e.clientY / window.innerHeight;
      
      const layers = document.querySelectorAll('.parallax-layer');
      layers.forEach(layer => {
        const speed = layer.getAttribute('data-speed') || 20;
        const x = (window.innerWidth - mouseX * speed) / 100;
        const y = (window.innerHeight - mouseY * speed) / 100;
        
        layer.style.transform = `translate(${x}px, ${y}px)`;
      });
    });
  }
});
