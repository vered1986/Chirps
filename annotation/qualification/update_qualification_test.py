import boto.mturk.connection as mt
import boto.mturk.question as mt_q


def main():

    # Connect to MTurk
    ACCESS_ID ='AKIAIFPEXD2UB7P3UILQ'
    SECRET_KEY = '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'
    # HOST = 'mechanicalturk.sandbox.amazonaws.com'
    HOST = 'mechanicalturk.amazonaws.com'

    connection = mt.MTurkConnection(aws_access_key_id=ACCESS_ID, aws_secret_access_key=SECRET_KEY, host=HOST)

    # Overview
    overview = mt_q.Overview()

    with open('instructions.txt') as f_in:
        instructions = f_in.read()

    overview.append_field('FormattedContent', '<![CDATA[%s]]>' % instructions)
    overview.append_field('Title', 'Answer the following questions:')

    # Question form
    question_form = mt_q.QuestionForm()
    question_form.append(overview)

    with open('questions.txt') as f_in:
        questions = [line.strip() for line in f_in]

    answers = [('Yes', 'yes'), ('No', 'no')]

    for i, question in enumerate(questions):

        qc = mt_q.QuestionContent()
        qc.append_field('FormattedContent', '<![CDATA[%s]]>' % question)
        fta = mt_q.SelectionAnswer(min=1, max=1, style='radiobutton', selections=answers, type='text', other=False)
        q = mt_q.Question(identifier='q%d' % (i + 1), content=qc, answer_spec=mt_q.AnswerSpecification(fta), is_required=True)
        question_form.append(q)

    # Build the answer key
    with open('answer_key.xml') as f_in:
        answer_key = f_in.read()

    # Update the qualification type
    connection.update_qualification_type('3KED7M8JSNE9I8HR49X08ZGF8EA6FS',
                                         description='This worker is qualified to answer HITs about English language semantics.',
                                         status='Active', test=question_form, answer_key=answer_key, test_duration=600)

if __name__ == '__main__':
    main()