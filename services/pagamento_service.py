import stripe
import secrets
import string
from datetime import datetime

# Configurar Stripe (substitua pela sua chave)
stripe.api_key = 'sua_chave_stripe_aqui'


def _random_digits(length):
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def gerar_boleto(pagamento, aluno):
    """Gera um boleto bancário"""
    
    # Exemplo com Stripe
    try:
        # Criar uma intenção de pagamento com boleto
        payment_intent = stripe.PaymentIntent.create(
            amount=int(pagamento.valor * 100),
            currency='brl',
            payment_method_types=['boleto'],
            payment_method_options={
                'boleto': {
                    'expires_after_days': 3,
                }
            },
            metadata={
                'aluno_id': aluno.id,
                'pagamento_id': pagamento.id,
                'referencia': pagamento.referencia
            }
        )
        
        # Em produção, você precisará obter os dados do boleto do webhook
        # Este é um exemplo simplificado
        return {
            'linha_digitavel': _random_digits(47),
            'codigo_barras': _random_digits(44),
            'link': f"https://pagamento.exemplo.com/boleto/{pagamento.id}",
            'payment_intent_id': payment_intent.id
        }
    
    except Exception as e:
        print(f"Erro ao gerar boleto: {e}")
        return None

def processar_pagamento_webhook(data):
    """Processa webhook de confirmação de pagamento"""
    from database import db, Pagamento
    
    # Verificar assinatura do webhook (importante para segurança)
    # ...
    
    payment_intent_id = data.get('payment_intent_id')
    status = data.get('status')
    
    if status == 'succeeded':
        pagamento = Pagamento.query.filter_by(payment_intent_id=payment_intent_id).first()
        
        if pagamento:
            pagamento.status = 'Pago'
            pagamento.data_pagamento = datetime.utcnow()
            db.session.commit()
            return True
    
    return False