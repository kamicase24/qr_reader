from flask import render_template
from app.retails import bp
from app.extensions import Base, db
from sqlalchemy import func, case
from sqlalchemy.orm import Session




@bp.route('/ripley/')
def ripley():

    session = Session(db.engine)
    QueryInput = Base.classes.get('QueryInput')
    RipleyResult = Base.classes.get('RipleyResult')
    RipleyDelivery = Base.classes.get('RipleyDelivery')

    cross_table = session.query(
        QueryInput.id.label('QueryInput_id'),
        QueryInput.key_words_search.label('QueryInput_key_words_search'),
        RipleyResult.QueryInput_id.label('RipleyResult_QueryInput_id'),
        RipleyResult.id.label('RipleyResult_id'),
        RipleyResult.part_number.label('RipleyResult_part_number'),
        RipleyResult.name.label('RipleyResult_name'),
        RipleyResult.url.label('RipleyResult_url'),
        case(
            (RipleyResult.is_marketplace_product == 0, '1P'),
            else_='3P'
        ).label('RipleyResult_etq_seller'),
        RipleyResult.scrap_ini.label('RipleyResult_scrap_ini'),
        RipleyDelivery.value.label('RipleyDelivery_value'),
        func.min(RipleyDelivery.closest_date).label('RipleyDelivery_closest_date'),
        # RipleyDelivery.discount_delivery.label('RipleyDelivery_discount_delivery'),

        case(
            (RipleyDelivery.discount_delivery == None, 0.00),
            else_=RipleyDelivery.discount_delivery
        ).label('RipleyDelivery_discount_delivery'),

        case(
            (
                RipleyDelivery.value - case(
                    (RipleyDelivery.discount_delivery == None, 0.00),
                    else_=RipleyDelivery.discount_delivery
                ) < 0.00,
                0.00
            ),
            else_=RipleyDelivery.value - case(
                (RipleyDelivery.discount_delivery == None, 0.00),
                else_=RipleyDelivery.discount_delivery
            )
        ).label('RipleyDelivery_value_conFlete'),
        
    ).join(
        RipleyResult, QueryInput.id == RipleyResult.QueryInput_id
    ).join(
        RipleyDelivery, RipleyResult.id == RipleyDelivery.RipleyResult_id
    ).filter(
        func.date(QueryInput.created_at) == func.current_date(),
        func.date(RipleyResult.created_at) == func.current_date(),        
    ).group_by(
        QueryInput.id,
        QueryInput.key_words_search,
        RipleyResult.QueryInput_id,
        RipleyResult.id,
        RipleyResult.part_number,
        RipleyResult.name,
        RipleyResult.url,
        RipleyResult.is_marketplace_product,
        RipleyResult.scrap_ini,
        RipleyDelivery.value,
        RipleyDelivery.discount_delivery,
    ).all()

    session.close()
    return render_template('retails/ripley.html', 
        cross_table=cross_table
    )