
fields = {
    "projects": ['id','created', 'updated','createdBy(id)','shortName', 'description', 'leader(id)', 'archived', 'fromEmail', 'replyToEmail', 'template', 'iconUrl',
               'name', 'Priority', 'Stage', 'customFields(id)'],

    "users" : ['id','created', 'updated', 'login', 'fullName', 'email', 'jabberAccountName', 'ringId', 'guest', 'online', 'banned',
              'tags(id)', 'savedQueries(id)', 'avatarUrl', 'profiles(id)'],

    "array_of_issuecomments": ['text', 'usesMarkdown', 'textPreview', 'created', 'updated', 'author(id,fullName)',
                              'attachments(name,created,updated,size,extension,charset,mimeType,metaData,draft,removed,'
                              'base64Content,url,thumbnailURL)'],

    "array_of_issuecustomfields": ['name', 'id',
                                  'projectCustomField(id,field(id,name)),value(avatarUrl,buildLink,color(id),fullName,'
                                  'id,isResolved,localizedName,login,minutes,name,presentation,text)'],

    "issuevoters": ['hasVote', 'original(id,fullName)', 'duplicate(issue(idReadable),user(id,fullName))'],

    "issuewatchers": ['hasStar',
                     'issueWatchers(user(id,fullName),issue(idReadable),isStarred),duplicateWatchers(user(id,fullName),'
                     'issue(idReadable),isStarred)'],
    "array_of_issueattachments": ['name', 'author(id,fullName)', 'created', 'updated', 'size', 'extension', 'charset',
                                 'mimeType', 'metaData', 'draft', 'removed', 'base64Content', 'url',
                                 'issue(idReadable)', 'comment(name)', 'thumbnailURL'],

    "issuelink": ['direction',
                 'linkType(name,localizedName,sourceToTarget,localizedSourceToTarget,targetToSource,'
                 'localizedTargetToSource,directed,aggregation,readOnly),issues(idReadable),trimmedIssues(idReadable)'],

    "externalissue": ['name', 'url', 'key'],

    "activities": ["id","author(id)","timestamp","added(id)","target(id)"],

    "workItems": ['id','author(id)','creator(id)','text','textPreview','type(id)','created', 'updated',
            'duration(minutes)', 'date', 'issue(id)','usesMarkdown'],

    "issues": ['id','idReadable', 'created', 'updated', 'resolved', 'numberInProject', 'project(id)', 'summary', 'description',
            'usesMarkdown', 'wikifiedDescription',
            'reporter(id)', 'updater(id)', 'draftOwner', 'isDraft', 'visibility(id)', 'votes', 'comments(id)', 'commentsCount',
            'externalIssue(id, key, url, name)', 'customFields(id)', 'voters(id)', 'watchers(id)',
            'attachments(id)', 'subtasks(id)', 'parent(id)'],


    "dates": ["updated","created","date","resolved"],

    "admin": ["projects","users"]
}


def all_nested_fields():
    # field types
    project = ['shortName', 'description', 'leader', 'archived', 'fromEmail', 'replyToEmail', 'template', 'iconUrl',
               'name', 'id', 'Priority', 'Stage']
    user = ['id', 'login', 'fullName', 'email', 'jabberAccountName', 'ringId', 'guest', 'online', 'banned',
            'tags(name,untagOnResolve)', 'savedQueries', 'avatarUrl', 'profiles']
    array_of_issuecomments = ['text', 'usesMarkdown', 'textPreview', 'created', 'updated', 'author(id,fullName)',
                              'attachments(name,created,updated,size,extension,charset,mimeType,metaData,draft,removed,'
                              'base64Content,url,thumbnailURL)']
    array_of_issuecustomfields = ['name', 'id',
                                  'projectCustomField(id,field(id,name)),value(avatarUrl,buildLink,color(id),fullName,'
                                  'id,isResolved,localizedName,login,minutes,name,presentation,text)']
    issuevoters = ['hasVote', 'original(id,fullName)', 'duplicate(issue(idReadable),user(id,fullName))']
    issuewatchers = ['hasStar',
                     'issueWatchers(user(id,fullName),issue(idReadable),isStarred),duplicateWatchers(user(id,fullName),'
                     'issue(idReadable),isStarred)']
    array_of_issueattachments = ['name', 'author(id,fullName)', 'created', 'updated', 'size', 'extension', 'charset',
                                 'mimeType', 'metaData', 'draft', 'removed', 'base64Content', 'url',
                                 'issue(idReadable)', 'comment(name)', 'thumbnailURL']
    issuelink = ['direction',
                 'linkType(name,localizedName,sourceToTarget,localizedSourceToTarget,targetToSource,'
                 'localizedTargetToSource,directed,aggregation,readOnly),issues(idReadable),trimmedIssues(idReadable)']
    externalissue = ['name', 'url', 'key']
    return {'Project': project, 'User': user, 'ArrayofIssueComments': array_of_issuecomments,
            'ArrayofIssueCustomFields': array_of_issuecustomfields, 'IssueVoters': issuevoters,
            'IssueWatchers': issuewatchers, 'ArrayofIssueAttachments': array_of_issueattachments,
            'ArrayofIssueLinks': issuelink, 'ExternalIssue': externalissue}


def all_issue_fields():
    return ['idReadable', 'created', 'updated', 'resolved', 'numberInProject', 'project', 'summary', 'description',
            'usesMarkdown', 'wikifiedDescription',
            'reporter', 'updater', 'draftOwner', 'isDraft', 'visibility', 'votes', 'comments', 'commentsCount',
            'externalIssue', 'customFields', 'voters', 'watchers',
            'attachments', 'subtasks', 'parent']


def all_workItems_fields():
    return ['id','author(id)','creator(id)','text','textPreview','type(id)','created', 'updated',
            'duration(minutes)', 'date', 'issue(id)','usesMarkdown']


def all_field_types():
    return {'idReadable': 'Long', 'created': 'Long', 'updated': 'Long', 'resolved': 'Long', 'numberInProject': 'Long',
            'project': 'Project', 'summary': 'String',
            'description': 'String', 'usesMarkdown': 'Boolean', 'wikifiedDescription': 'String', 'reporter': 'User',
            'updater': 'User', 'draftOwner': 'User',
            'isDraft': 'Boolean', 'visibility': 'Visibility', 'votes': 'Int', 'comments': 'ArrayofIssueComments',
            'commentsCount': 'Long', 'links': 'ArrayofIssueLinks',
            'externalIssue': ' ExternalIssue', 'customFields': 'ArrayofIssueCustomFields', 'voters': ' IssueVoters',
            'watchers': 'IssueWatchers',
            'attachments': 'ArrayofIssueAttachments', 'subtasks': 'ArrayofIssueLinks', 'parent': 'ArrayofIssueLinks'}


def make_issues_fields_query():
    nested_fields = all_nested_fields()
    issue_fields = all_issue_fields()
    field_types = all_field_types()

    query = 'fields='
    nested_keys = nested_fields.keys()

    for i, field in enumerate(issue_fields):
        query += field
        if field_types[field] in nested_keys:
            query += '(' + ",".join(nested_fields[field_types[field]]) + ')'
        if i != len(issue_fields) - 1:
            query += ','
    return query

def make_workItems_fields_query():

    query = 'fields=' + ",".join(all_workItems_fields())

    return query

def fields_query(datatype):
    if datatype in fields:
        return 'fields=' + ",".join(fields[datatype])
    return ""

def make_projects_fields_query():
    nested_fields = all_nested_fields()
    query = 'fields=' + ",".join(nested_fields['Project'])

    return query




def make_projects_fields_query_customfields():
    return 'fields=field(aliases,isAutoAttached,isUpdateable,name,id),canBeEmpty,isPublic,id'


def make_users_fields_query():
    nested_fields = all_nested_fields()
    query = 'fields=' + ",".join(nested_fields['User'])
    return query
